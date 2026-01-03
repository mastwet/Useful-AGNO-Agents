from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.local_file_system import LocalFileSystemTools
from agno.tools.shell import ShellTools
import os
from pathlib import Path
import platform

# 设置DeepSeek API密钥
os.environ["DEEPSEEK_API_KEY"] = ""


class DesktopCleanupAgent:
    def __init__(self):
        # 检测操作系统
        self.system = platform.system().lower()
        self.desktop_path = str(Path.home() / "Desktop")

        # 初始化本地文件系统工具
        self.fs_tools = LocalFileSystemTools(
            target_directory="./")

        # 初始化shell工具
        self.shell_tools = ShellTools()

        # 创建桌面清理大师Agent - 使用DeepSeek
        self.agent = Agent(
            model=DeepSeek(id="deepseek-chat"),
            instructions=[
                "你是一个专业的桌面清理大师智能体，专门帮助用户整理Desktop目录下的文件和文件夹。",
                "重要规则：完全忽略所有桌面快捷方式，不要对它们进行任何操作！",
                f"当前操作系统: {self.system}",
                "快捷方式识别规则：",
                "- Windows (.lnk 文件): 忽略所有 .lnk 扩展名的文件",
                "- macOS (别名文件): 忽略所有具有别名属性的文件，通常没有特殊扩展名但可通过系统属性识别",
                "- Linux (.desktop 文件): 忽略所有 .desktop 扩展名的文件",
                "- 任何指向应用程序、网站或系统位置的快捷方式文件都要忽略",
                "工作流程：1) 分析桌面（排除快捷方式），2) 提出整理方案（不含快捷方式），3) 执行安全移动操作",
                "对于文件夹：直接移动整个文件夹到目标目录，不要展开处理内部文件",
                "对于文件：根据文件类型移动到对应的分类目录",
                "永远不要删除任何文件或文件夹，只进行移动操作，且完全跳过快捷方式",
                "文件分类建议：",
                "- 文档类文件(.pdf, .doc, .docx, .txt, .xlsx, .pptx等) -> 'Documents'目录",
                "- 图片类文件(.jpg, .png, .gif, .jpeg, .svg等) -> 'Images'目录",
                "- 视频类文件(.mp4, .avi, .mov, .mkv等) -> 'Videos'目录",
                "- 音频类文件(.mp3, .wav, .flac, .m4a等) -> 'Audio'目录",
                "- 程序安装包(.exe, .dmg, .msi, .pkg等) -> 'Installers'目录",
                "- 压缩包类文件(.zip, .rar, .7z, .tar.gz等) -> 'Archives'目录",
                "- 项目文件夹 -> 'Projects'目录",
                "- 其他无法明确分类的文件 -> 'Others'目录",
                "快捷方式处理原则：",
                "- 在分析阶段就识别并排除所有快捷方式",
                "- 在整理方案中明确说明哪些文件被识别为快捷方式并已忽略",
                "- 绝不移动、重命名或修改任何快捷方式文件",
                "- 保持所有快捷方式在桌面原位置不变",
                "输出格式要清晰，使用Markdown格式展示当前状态和建议方案。"
            ],
            tools=[self.fs_tools, self.shell_tools],
            markdown=True
        )

    async def identify_shortcuts(self):
        """识别并列出所有快捷方式"""
        shortcut_identification_prompt = f"""
        请识别Desktop目录中的所有快捷方式文件，并明确列出它们。
        操作系统: {self.system}

        识别方法：
        - Windows: 查找所有 .lnk 扩展名的文件
        - macOS: 查找别名文件（可能需要使用系统命令识别）
        - Linux: 查找所有 .desktop 扩展名的文件

        使用LocalFileSystemTools工具来列出Desktop目录的所有文件，
        然后识别哪些是快捷方式。
        """
        return self.agent.run(shortcut_identification_prompt)

    async def analyze_desktop_excluding_shortcuts(self):
        """分析桌面状态，明确排除快捷方式"""
        analysis_prompt = f"""
        请分析用户Desktop目录的当前状态，但完全排除所有快捷方式文件：

        1. 使用LocalFileSystemTools工具列出所有非快捷方式的文件和文件夹
        2. 对每个项目进行分类和描述
        3. 识别系统文件夹或重要文件夹（不要移动的）
        4. 统计各类可整理文件和文件夹的数量分布
        5. 评估当前桌面的混乱程度（不考虑快捷方式）

        Desktop路径: {self.desktop_path}
        """
        return self.agent.run(analysis_prompt)

    async def propose_cleanup_plan_excluding_shortcuts(self):
        """提出整理方案，明确说明快捷方式被忽略"""
        proposal_prompt = """
        基于之前的分析（已排除快捷方式），请提出详细的桌面整理方案：

        **处理原则：**
        - 所有快捷方式文件已被识别并完全忽略
        - 只对非快捷方式的文件和文件夹进行整理
        - 文件夹直接整体移动，文件按类型分类移动
        - 使用LocalFileSystemTools和ShellTools来执行操作

        请按以下格式输出方案：

        ### 🚫 已忽略的快捷方式
        [列出之前识别的快捷方式，说明它们将保持在桌面原位置]

        ### 📁 文件夹整理计划
        - 移动 `项目文件夹` → `Projects/项目文件夹`
        - 移动 `照片_2023` → `Images/照片_2023`

        ### 📄 文件整理计划  
        - 移动 `report.pdf` → `Documents/report.pdf`
        - 移动 `vacation.jpg` → `Images/vacation.jpg`
        """
        return self.agent.run(proposal_prompt)

    async def execute_cleanup_excluding_shortcuts(self, confirmed_plan):
        """执行整理计划，确保不触碰快捷方式"""
        self.fs_tools.write = True

        execution_prompt = f"""
        用户已确认整理方案。请安全执行移动操作，严格遵守以下规则：

        1. 绝对不要对任何快捷方式文件进行操作（.lnk, .desktop, macOS别名等）
        2. 只处理方案中明确列出的非快捷方式文件和文件夹
        3. 首先使用ShellTools创建所有需要的目标目录
        4. 然后使用LocalFileSystemTools或ShellTools移动文件和文件夹
        5. 每个操作都要验证成功

        整理方案：
        {confirmed_plan}

        请详细记录执行过程，特别确认没有对任何快捷方式进行操作。
        """
        result = await self.agent.run(execution_prompt)
        self.fs_tools.write = False
        return result


# 使用示例
async def main():
    # 创建桌面清理大师（使用DeepSeek）
    cleanup_agent = DesktopCleanupAgent()

    print("🔍 正在检测桌面快捷方式...")
    shortcuts = await cleanup_agent.identify_shortcuts()
    print(shortcuts)

    print("\n🔍 正在分析桌面（排除快捷方式）...")
    analysis = await cleanup_agent.analyze_desktop_excluding_shortcuts()
    print(analysis)

    print("\n📋 正在生成整理方案...")
    proposal = await cleanup_agent.propose_cleanup_plan_excluding_shortcuts()
    print(proposal)

    user_confirm = input("\n是否确认执行整理方案？(yes/no): ")

    if user_confirm.lower() in ['yes', 'y']:
        print("\n🧹 开始执行整理...")
        result = await cleanup_agent.execute_cleanup_excluding_shortcuts(proposal)
        print(result)
    else:
        print("整理已取消。")

    print("\n✅ 整理完成！")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
