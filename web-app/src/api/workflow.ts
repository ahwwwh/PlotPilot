/**
 * 子项目 8：工作流 / 长任务 / 一致性 / 故事线
 * 后端路由实现见 `docs/superpowers/plans/2026-04-02-subproject-8-frontend-extensions.md`
 */
import { apiClient } from './config'
import type { JobCreateResponse, JobStatusResponse } from '../types/api'

export interface GenerateChapterWithContextPayload {
  chapter_number: number
  outline: string
}

/** 与 `interfaces/api/v1/generation.py` GenerateChapterResponse 对齐 */
export interface ConsistencyIssueDTO {
  type: string
  severity: string
  description: string
  location: number
}

export interface ConsistencyReportDTO {
  issues: ConsistencyIssueDTO[]
  warnings: ConsistencyIssueDTO[]
  suggestions: string[]
}

export interface GenerateChapterWorkflowResponse {
  content: string
  consistency_report: ConsistencyReportDTO
  token_count: number
}

export const workflowApi = {
  /**
   * POST /api/v1/novels/{novel_id}/generate-chapter
   * AutoNovelGenerationWorkflow：上下文 + 生成 + 一致性报告（子项目 8）
   */
  generateChapterWithContext: (novelId: string, data: GenerateChapterWithContextPayload) =>
    apiClient.post<GenerateChapterWorkflowResponse>(`/novels/${novelId}/generate-chapter`, data) as Promise<GenerateChapterWorkflowResponse>,

  /** GET /api/v1/novels/{novel_id}/consistency-report */
  getConsistencyReport: (novelId: string, chapter?: number) =>
    apiClient.get<unknown>(`/novels/${novelId}/consistency-report`, {
      params: chapter != null ? { chapter } : {},
    }) as Promise<unknown>,

  /** GET /api/v1/novels/{novel_id}/storylines */
  getStorylines: (novelId: string) =>
    apiClient.get<unknown>(`/novels/${novelId}/storylines`) as Promise<unknown>,

  /** POST /api/v1/novels/{novel_id}/plot-arc（body 含 key_points 等，见后端 CreatePlotArcRequest） */
  createPlotArc: (novelId: string, data: Record<string, unknown>) =>
    apiClient.post<unknown>(`/novels/${novelId}/plot-arc`, data) as Promise<unknown>,

  /**
   * 以下 Job 路由 **后端尚未实现**（`interfaces` 无 `/jobs`），调用会 404。
   * 实现后可保留这些方法；未实现前工作台「结构规划/撰稿」会失败。
   */
  /** POST /api/v1/novels/{novel_id}/jobs/plan */
  startPlanJob: (novelId: string, dryRun = false, mode: 'initial' | 'revise' = 'initial') =>
    apiClient.post<JobCreateResponse>(`/novels/${novelId}/jobs/plan`, {
      dry_run: dryRun,
      mode,
    }) as Promise<JobCreateResponse>,

  /** POST /api/v1/novels/{novel_id}/jobs/write */
  startWriteJob: (
    novelId: string,
    from: number,
    to?: number,
    dryRun = false,
    continuity = false
  ) =>
    apiClient.post<JobCreateResponse>(`/novels/${novelId}/jobs/write`, {
      from_chapter: from,
      to_chapter: to,
      dry_run: dryRun,
      continuity,
    }) as Promise<JobCreateResponse>,

  /** POST /api/v1/novels/{novel_id}/jobs/run */
  startRunJob: (novelId: string, dryRun = false, continuity = false) =>
    apiClient.post<JobCreateResponse>(`/novels/${novelId}/jobs/run`, {
      dry_run: dryRun,
      continuity,
    }) as Promise<JobCreateResponse>,

  /** POST /api/v1/novels/{novel_id}/jobs/export */
  exportBook: (novelId: string) =>
    apiClient.post<unknown>(`/novels/${novelId}/jobs/export`, {}) as Promise<unknown>,

  /** GET /api/v1/jobs/{job_id} */
  getJobStatus: (jobId: string) =>
    apiClient.get<JobStatusResponse>(`/jobs/${jobId}`) as Promise<JobStatusResponse>,

  /** POST /api/v1/jobs/{job_id}/cancel */
  cancelJob: (jobId: string) =>
    apiClient.post<{ ok: boolean }>(`/jobs/${jobId}/cancel`, {}) as Promise<{ ok: boolean }>,
}
