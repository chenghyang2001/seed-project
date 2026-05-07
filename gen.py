"""
gen.py — PNG 圖片目錄 → index.html 檢視器產生器

讀取指定目錄下的 PNG 圖片，將資料注入 HTML 模板（simple 或 grouped），
輸出可直接瀏覽的 index.html。

用法：
    python gen.py --mode simple  --title "AIHCR 診斷圖"  --dir ./images   --accent cyan
    python gen.py --mode grouped --title "OpenClaw 簡報" --dir ./chapters --accent blue
"""

import argparse
import json
import sys
from pathlib import Path

# 主題色票：hex / rgb（CSS rgba 用）/ light（漸層用）
THEMES = {
    "cyan":   {"hex": "#38bdf8", "rgb": "56,189,248",   "light": "#7dd3fc"},
    "blue":   {"hex": "#60a5fa", "rgb": "96,165,250",   "light": "#93c5fd"},
    "green":  {"hex": "#4ade80", "rgb": "74,222,128",   "light": "#86efac"},
    "amber":  {"hex": "#fbbf24", "rgb": "251,191,36",   "light": "#fcd34d"},
    "purple": {"hex": "#a78bfa", "rgb": "167,139,250",  "light": "#c4b5fd"},
}

# 模板位置以 gen.py 自身所在目錄為基準，確保跨平台可攜
SCRIPT_DIR = Path(__file__).resolve().parent


def inject_template(template_path: Path, title: str, theme: dict, data_json: str) -> str:
    """讀取 HTML 模板，替換全部五個 placeholder，回傳完整 HTML 字串。"""
    if not template_path.exists():
        print(f"錯誤：找不到模板檔案 {template_path}", file=sys.stderr)
        sys.exit(1)

    html = template_path.read_text(encoding="utf-8")

    # 依序替換五個佔位符（replace_all 確保同一佔位符多次出現也全數換掉）
    html = html.replace("__TITLE__",        title)
    html = html.replace("__ACCENT__",       theme["hex"])
    html = html.replace("__ACCENT_RGB__",   theme["rgb"])
    html = html.replace("__ACCENT_LIGHT__", theme["light"])
    html = html.replace("__DATA__",         data_json)

    return html


def build_simple(img_dir: Path, output_path: Path) -> str:
    """
    Simple 模式：遞迴掃描 img_dir 下的 *.png，
    依完整路徑字母順序排序，建立扁平清單 JSON。
    圖片路徑以 output_path 所在目錄為基準（相對路徑）。
    """
    output_dir = output_path.parent

    # 遞迴搜集所有 PNG，按完整路徑字母排序
    all_pngs = sorted(img_dir.rglob("*.png"))

    if not all_pngs:
        print(f"警告：在 {img_dir} 下找不到任何 PNG 圖片，仍將輸出空白 HTML。", file=sys.stderr)

    images = []
    for png in all_pngs:
        # 換算成相對於 output 所在目錄的路徑，統一使用正斜線（瀏覽器路徑需求）
        rel = png.relative_to(output_dir).as_posix()
        label = png.stem  # 去掉副檔名的檔案名稱作為標籤
        images.append({"file": rel, "label": label})

    return json.dumps(images, ensure_ascii=False)


def build_grouped(img_dir: Path, output_path: Path) -> str:
    """
    Grouped 模式：掃描 img_dir 的直屬子目錄，每個子目錄形成一個群組。
    跳過 PNG 數量為零的子目錄。
    圖片路徑以 output_path 所在目錄為基準（相對路徑）。
    """
    output_dir = output_path.parent

    # 只取直屬子目錄，按名稱字母排序
    subdirs = sorted([p for p in img_dir.iterdir() if p.is_dir()])

    groups = []
    for subdir in subdirs:
        pngs = sorted(subdir.glob("*.png"))
        if not pngs:
            # 跳過沒有 PNG 的子目錄，避免產出空群組干擾使用者
            continue

        rel_images = [png.relative_to(output_dir).as_posix() for png in pngs]
        groups.append({"label": subdir.name, "images": rel_images})

    if not groups:
        print(
            f"警告：在 {img_dir} 下找不到含有 PNG 的子目錄，仍將輸出空白 HTML。",
            file=sys.stderr,
        )

    return json.dumps(groups, ensure_ascii=False)


def parse_args() -> argparse.Namespace:
    """設定並解析 CLI 參數。"""
    parser = argparse.ArgumentParser(
        description="將 PNG 圖片目錄產生為可瀏覽的 index.html 檢視器"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=["simple", "grouped"],
        help="simple：扁平清單；grouped：依子目錄分群（側邊欄）",
    )
    parser.add_argument("--title", required=True, help="頁面標題（顯示於 header）")
    parser.add_argument(
        "--dir",
        required=True,
        help="圖片根目錄（simple 模式：含 PNG 的目錄；grouped 模式：含子目錄的目錄）",
    )
    parser.add_argument(
        "--accent",
        default="cyan",
        choices=list(THEMES.keys()),
        help="主題色（預設：cyan）",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="輸出 HTML 路徑（預設：<dir>/index.html）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    img_dir = Path(args.dir).resolve()

    # 確認來源目錄存在，否則立即終止並說明原因
    if not img_dir.exists() or not img_dir.is_dir():
        print(f"錯誤：目錄不存在或不是有效目錄：{img_dir}", file=sys.stderr)
        sys.exit(1)

    # 決定輸出路徑；未指定時預設放在圖片目錄下
    output_path = Path(args.output).resolve() if args.output else img_dir / "index.html"

    theme = THEMES[args.accent]

    try:
        if args.mode == "simple":
            template_path = SCRIPT_DIR / "templates" / "simple.html"
            data_json = build_simple(img_dir, output_path)
        else:
            template_path = SCRIPT_DIR / "templates" / "grouped.html"
            data_json = build_grouped(img_dir, output_path)

        html_content = inject_template(template_path, args.title, theme, data_json)

        # 確保輸出目錄存在（若 --output 指定了不存在的目錄）
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_path.write_text(html_content, encoding="utf-8")
        print(f"完成：{output_path}")

    except SystemExit:
        # inject_template 或其他函式已印出錯誤訊息，直接傳遞 exit code
        raise
    except Exception as e:
        print(f"錯誤：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
