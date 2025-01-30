#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import OrderedDict

BASE_FILE = "base.conf"
DIY_FILE = "diy.conf"
SUB_FILE = "sub.txt"
OUTPUT_FILE = "funnysurge.conf"

def parse_conf(filename):
    """
    将 Surge 配置文件按段落 [SectionName] 拆分，
    返回 (section_order, sections_map)
    - section_order: [ 'GLOBAL', 'General', 'Proxy Group', 'Rule', ... ]
    - sections_map:  { 'GLOBAL': [...lines...], 'General': [...], ... }
    注意：在出现第一个 [Section] 之前的行，算作 'GLOBAL' 段落
    """
    section_order = []
    sections = OrderedDict()

    current_section = "GLOBAL"
    sections[current_section] = []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line_stripped = line.rstrip("\n")
            # 检查是否匹配 [SectionName]
            if line_stripped.startswith("[") and line_stripped.endswith("]"):
                # 提取中间的名称
                section_name = line_stripped[1:-1].strip()
                # 新建一个段落
                current_section = section_name
                if current_section not in sections:
                    sections[current_section] = []
                section_order.append(current_section)
            else:
                # 普通行，加入当前段落
                sections[current_section].append(line_stripped)
    # 如果GLOBAL段落只有""空行，也原样留着，不做特殊处理
    # 但要注意如果 "GLOBAL" 没有任何有效行，也会是空。
    # 这都可以灵活处理。
    if "GLOBAL" not in section_order and len(sections["GLOBAL"]) > 0:
        # 如果 GLOBAL 里确实存了点东西，就把它加到开头
        section_order.insert(0, "GLOBAL")

    return section_order, sections


def merge_sections(base_order, base_sections, diy_order, diy_sections):
    """
    把 diy_sections 的内容合并到 base_sections：
      - 如果段落同名，则将 diy 的内容（在前面加一行 "# DIY"）插在 base 对应段落最前面；
      - 如果 base 没有这个段落，则在最后添加一个新段落。
    返回合并后的 (new_order, new_sections)
    """
    # 我们直接在 base 的结构上修改即可
    new_order = base_order[:]
    new_sections = OrderedDict()
    for sec in new_order:
        new_sections[sec] = base_sections[sec][:]  # 拷贝一份 list

    # 先处理 diy 中所有段落
    for sec in diy_order:
        diy_lines = diy_sections[sec]
        if sec in new_sections:
            # 同名段落，插在最前面：加一行 "# DIY"
            # 注意，如果 diy_lines 本身为空则没什么插的
            if diy_lines:
                merged = ["# DIY"] + diy_lines + new_sections[sec]
                new_sections[sec] = merged
        else:
            # base 没有该段落，需要新增
            new_order.append(sec)
            new_sections[sec] = diy_lines[:]

    return new_order, new_sections


def process_proxy_group(sections, sub_list, sub_urls):
    """
    在 sections 中找到 "Proxy Group"，对其内容：
    1) 替换 include-other-group=""
    2) 在末尾添加
       Sub-1 = select, policy-path=..., hidden=true
       ...
    """
    sec_name = "Proxy Group"
    if sec_name not in sections:
        return
    lines = sections[sec_name]
    new_lines = []
    for ln in lines:
        if "include-other-group=\"\"" in ln:
            ln = ln.replace('include-other-group=""', f'include-other-group="{sub_list}"')
        new_lines.append(ln)
    # 在末尾加上 Sub-n
    for i in range(len(sub_urls)):
        idx = i + 1
        url = sub_urls[idx - 1]
        new_lines.append(f"Sub-{idx} = select, policy-path={url}, hidden=true")
    sections[sec_name] = new_lines


def main():
    # 1) 读取 sub.txt，生成 sub_urls & 拼接 sub_list
    sub_urls = []
    with open(SUB_FILE, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if url:
                sub_urls.append(url)

    # 形如 "Sub-1, Sub-2, Sub-3"
    sub_list = ", ".join(f"Sub-{i+1}" for i in range(len(sub_urls)))

    # 2) 解析 base.conf
    base_order, base_sections = parse_conf(BASE_FILE)

    # 3) 解析 diy.conf
    diy_order, diy_sections = parse_conf(DIY_FILE)

    # 4) 合并 diy -> base
    merged_order, merged_sections = merge_sections(base_order, base_sections,
                                                   diy_order, diy_sections)

    # 5) 处理 [Proxy Group] 的订阅逻辑
    process_proxy_group(merged_sections, sub_list, sub_urls)

    # 6) 写出到 funnysurge.conf
    #    要求在 [Rule] 段落前空一行，其他段照原顺序输出
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for i, sec in enumerate(merged_order):
            # GLOBAL 段：如果有内容，就直接写
            if sec == "GLOBAL":
                for line in merged_sections[sec]:
                    out.write(line + "\n")
                continue

            # 在 [Rule] 段落前插入一个空行
            if sec == "Rule":
                out.write("\n")

            out.write(f"[{sec}]\n")
            for line in merged_sections[sec]:
                out.write(line + "\n")

    print(f"合并完成，输出 => {OUTPUT_FILE}")


if __name__ == "__main__":
    # 如果想要灵活指定文件名，可以在这里改或用命令行参数
    # 但此处简单起见，写死常量即可
    main()