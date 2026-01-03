from agno.agent import Agent
from agno.models.deepseek import DeepSeek
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# 设置 DeepSeek API 密钥
os.environ["DEEPSEEK_API_KEY"] = ""


def safe_split_markdown(content: str, max_chars: int = 4000) -> list:
    """安全分割 Markdown，强制切割超长行"""
    if not content.strip():
        return []
    chunks = []
    current = ""
    for line in content.split('\n'):
        while len(line) > max_chars:
            split_pos = max_chars
            search_start = max(0, max_chars - 50)
            for i in range(max_chars, search_start, -1):
                if line[i] in ' \t\n.,;:!?)]}':
                    split_pos = i + 1
                    break
            part = line[:split_pos]
            if current and len(current) + len(part) <= max_chars:
                current += part
            else:
                if current:
                    chunks.append(current)
                current = part
            line = line[split_pos:]
        if current and len(current) + 1 + len(line) > max_chars:
            chunks.append(current)
            current = line
        else:
            current = current + '\n' + line if current else line
    if current:
        chunks.append(current)
    return chunks


# 线程局部存储
thread_local = threading.local()


def create_translator():
    return Agent(
        model=DeepSeek(id="deepseek-chat"),
        markdown=True,
        instructions=[
            "你是一个专业学术翻译专家。将以下英文 Markdown 翻译为中文，严格保留所有格式（标题、列表、代码、公式、表格等）。只翻译文本，不改格式。输出必须是合法 Markdown，无额外说明。"
        ]
    )


def get_translator():
    if not hasattr(thread_local, "translator"):
        thread_local.translator = create_translator()
    return thread_local.translator


def translate_single_chunk(args):
    """关键修复：正确提取 RunOutput 的 .content"""
    idx, text = args
    if not text.strip():
        return idx, text

    try:
        translator = get_translator()
        prompt = f"请翻译以下 Markdown 片段为中文，严格保留格式：\n\n{text}"
        response = translator.run(prompt)

        # ✅ 正确方式：RunOutput 对象有 .content 属性
        if hasattr(response, 'content'):
            translated_text = response.content
        else:
            # 兜底：转为字符串（理论上不会触发）
            translated_text = str(response)

        return idx, translated_text
    except Exception as e:
        print(f"⚠️ 块 {idx + 1} 翻译失败，保留原文: {e}")
        return idx, text


def translate_paper_from_file(file_path: str, output_path: str, max_workers: int = 4):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.strip():
        raise ValueError("文件为空")

    print(f"📝 文件总字符数: {len(content)}")
    chunks = safe_split_markdown(content, max_chars=4000)
    print(f"📦 已分割为 {len(chunks)} 个块")

    results = [None] * len(chunks)
    tasks = [(i, chunk) for i, chunk in enumerate(chunks)]

    print(f"🚀 启动 {max_workers} 个线程进行翻译...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(translate_single_chunk, task) for task in tasks]
        for future in as_completed(futures):
            idx, translated = future.result()
            results[idx] = translated
            print(f"✅ 完成块 {idx + 1}/{len(chunks)}")

    # 合并结果（用 \n 连接更安全）
    full_translation = '\n'.join(results)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_translation)
    print(f"✅ 翻译完成！已保存至: {output_path}")


if __name__ == "__main__":
    input_file = "paper_en.md"
    output_file = "paper_zh.md"

    try:
        translate_paper_from_file(
            file_path=input_file,
            output_path=output_file,
            max_workers=4
        )
    except Exception as e:
        print(f"❌ 错误: {e}")
