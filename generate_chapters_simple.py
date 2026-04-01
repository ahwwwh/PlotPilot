#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Continue automated chapter generation from chapter 10 to 100"""
import asyncio
import httpx
import json
from datetime import datetime

async def generate_batch(from_ch: int, to_ch: int):
    url = "http://localhost:8007/api/v1/novels/novel-1775066530753/hosted-write-stream"
    payload = {
        "from_chapter": from_ch,
        "to_chapter": to_ch,
        "auto_save": True,
        "auto_outline": True
    }

    print(f"\n{'='*60}")
    print(f"Starting batch: Chapters {from_ch}-{to_ch}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    async with httpx.AsyncClient(timeout=600.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            if response.status_code != 200:
                text = await response.aread()
                print(f"ERROR: {text.decode()}")
                return False

            current_chapter = None
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        event = json.loads(line[6:])
                        event_type = event.get("type")

                        if event_type == "chapter_start":
                            current_chapter = event.get("chapter")
                            print(f"\nChapter {current_chapter} - Starting...")

                        elif event_type == "outline":
                            print(f"   Outline generated")

                        elif event_type == "phase":
                            phase = event.get("phase")
                            print(f"   Phase: {phase}")

                        elif event_type == "done":
                            word_count = len(event.get("content", ""))
                            print(f"   DONE: ~{word_count} characters")

                        elif event_type == "saved":
                            if event.get("ok"):
                                print(f"   SAVED successfully")
                            else:
                                print(f"   SAVE FAILED: {event.get('message')}")

                        elif event_type == "error":
                            print(f"   ERROR: {event.get('message')}")
                            return False

                    except json.JSONDecodeError:
                        pass

    print(f"\nBatch {from_ch}-{to_ch} completed!\n")
    return True

async def main():
    print("\n" + "="*60)
    print("Automated Chapter Generation System")
    print("="*60)

    # Generate in batches of 10 chapters
    batches = [
        (10, 19),
        (20, 29),
        (30, 39),
        (40, 49),
        (50, 59),
        (60, 69),
        (70, 79),
        (80, 89),
        (90, 100),
    ]

    for from_ch, to_ch in batches:
        success = await generate_batch(from_ch, to_ch)
        if not success:
            print(f"\nBatch {from_ch}-{to_ch} failed. Stopping.")
            break

        # Small delay between batches
        await asyncio.sleep(2)

    print("\n" + "="*60)
    print("All batches completed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
