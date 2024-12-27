#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re

def parse_surge_conf(conf_path):
    """
    Parse the Surge configuration file to get all node lines from the [Proxy] section.

    Returns a list where each element is in the format:
        "node_name=protocol,address,port,..."
    """
    in_proxy_section = False
    collected_lines = []  # Store parsed node lines (before or after merging)
    final_proxies = []    # Final complete node lines to return

    with open(conf_path, 'r', encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Check if entering [Proxy] section
            # (Case insensitive, can use lower() or regex)
            if re.match(r'^\[proxy\]', line, flags=re.IGNORECASE):
                in_proxy_section = True
                continue

            # If already in [Proxy] section and a new [xxx] section is found, exit
            if in_proxy_section and re.match(r'^\[.+\]', line):
                in_proxy_section = False
                continue

            # If still in [Proxy] section, process this line
            if in_proxy_section:
                # Check if need to merge with previous line
                if collected_lines:
                    # Check if previous line contains '='
                    # If no '=', might be a split line that needs merging
                    if '=' not in collected_lines[-1]:
                        # Append current line to previous line with a space in between
                        collected_lines[-1] = collected_lines[-1] + " " + line
                        continue
                    else:
                        # Previous line has =, check if current line might be a continuation
                        # Some subscriptions put node name on one line and =vmess... on next line
                        # In this case, if current line doesn't start with '[', try merging
                        if not line.startswith('[') and not '=' in line:
                            collected_lines[-1] = collected_lines[-1] + " " + line
                            continue
                        # Otherwise treat current line as new line
                        collected_lines.append(line)
                else:
                    # First addition
                    collected_lines.append(line)

    # At this point, collected_lines contains lines from [Proxy] section (possibly merged)
    # Let's check if any secondary merging is needed
    # Most merging is already done above, this is just for safety
    # Detailed logic omitted in this example

    # Filter for lines containing '=' as valid nodes
    for cl in collected_lines:
        if '=' in cl:
            final_proxies.append(cl.strip())
        else:
            # If still no =, likely invalid line/comment/empty line
            # Could try further merging, but example skips these
            pass

    return final_proxies


def classify_proxies(proxy_lines):
    """
    Classify nodes based on keywords in node names, returns:
    {
        "ALL": [ (node_name, complete_line) , ... ],
        "HK": [...],
        "SGP": [...],
        "TW":  [...],
        "JP":  [...],
        "USA": [...],
    }
    """
    # Predefined common region keywords, can be extended
    area_keywords = {
        "HK":   [r'Hong Kong', r'HK', r'HKG'],
        "SGP":  [r'Singapore', r'SGP'],
        "TW":   [r'Taiwan', r'TW', r'TWN'],
        "JP":   [r'Japan', r'JP', r'JPN'],
        "USA":  [r'United States', r'USA', r'US'],
    }

    # Classification results
    classified = {
        "ALL": [],
        "HK": [],
        "SGP": [],
        "TW":  [],
        "JP":  [],
        "USA": [],
    }

    for line in proxy_lines:
        # line format: "🇭🇰 ①Hong Kong | HKG [Unlock] x1.2{Ver6.1}=vmess,...."
        # Split
        left, right = line.split('=', 1)
        node_name = left.strip()  # Proxy name

        # Record in ALL
        classified["ALL"].append((node_name, line))

        # Determine region
        node_name_upper = node_name.upper()
        for area, keywords in area_keywords.items():
            # Match with any keyword to classify as that region
            for kw in keywords:
                if re.search(kw, node_name_upper, flags=re.IGNORECASE):
                    classified[area].append((node_name, line))
                    break  # Exit kw loop, avoid duplicate matching

    return classified


def generate_proxy_group_text(classified):
    """
    Generate text for groups in [Proxy Group] according to requirements.

    Requirements:
      1) Proxy
         - select mode
         - Include: "🇭🇰 HK" "🇸🇬 SGP" "🇨🇳 TW" "🇯🇵 JP" "🇺🇸 USA" "Auto" + all nodes
      2) Auto
         - url-test mode
         - Include all nodes
      3) AI
         - select mode
         - Include: "🇸🇬 SGP" "🇨🇳 TW" "🇯🇵 JP" "🇺🇸 USA"
      4) 🇭🇰 HK
         - url-test mode
         - Include HK related nodes
      5) 🇸🇬 SGP
         - url-test mode
         - Include SGP related nodes
      6) 🇨🇳 TW
         - url-test mode
         - Include TW related nodes
      7) 🇯🇵 JP
         - url-test mode
         - Include JP related nodes
      8) 🇺🇸 USA
         - url-test mode
         - Include USA related nodes

    Returns a string for writing to diy.conf.
    """

    # Extract node names
    all_nodes = [x[0] for x in classified["ALL"]]
    hk_nodes =  [x[0] for x in classified["HK"]]
    sgp_nodes = [x[0] for x in classified["SGP"]]
    tw_nodes  = [x[0] for x in classified["TW"]]
    jp_nodes  = [x[0] for x in classified["JP"]]
    usa_nodes = [x[0] for x in classified["USA"]]

    # 1) Proxy group (select)
    proxy_group_line = "Proxy = select, 🇭🇰 HK, 🇸🇬 SGP, 🇨🇳 TW, 🇯🇵 JP, 🇺🇸 USA, Auto"
    if all_nodes:
        proxy_group_line += ", " + ", ".join(all_nodes)

    # 2) Auto group (url-test, all nodes)
    auto_group_line = "Auto = url-test, " + ", ".join(all_nodes) + \
                      ", url=http://www.gstatic.com/generate_204, interval=300"

    # 3) AI group (select)
    ai_group_line = "AI = select, 🇸🇬 SGP, 🇨🇳 TW, 🇯🇵 JP, 🇺🇸 USA"

    # 4) 🇭🇰 HK group (url-test)
    hk_line = "🇭🇰 HK = url-test"
    if hk_nodes:
        hk_line += ", " + ", ".join(hk_nodes)
    hk_line += ", url=http://www.gstatic.com/generate_204, interval=300"

    # 5) 🇸🇬 SGP group (url-test)
    sgp_line = "🇸🇬 SGP = url-test"
    if sgp_nodes:
        sgp_line += ", " + ", ".join(sgp_nodes)
    sgp_line += ", url=http://www.gstatic.com/generate_204, interval=300"

    # 6) 🇨🇳 TW group (url-test)
    tw_line = "🇨🇳 TW = url-test"
    if tw_nodes:
        tw_line += ", " + ", ".join(tw_nodes)
    tw_line += ", url=http://www.gstatic.com/generate_204, interval=300"

    # 7) 🇯🇵 JP group (url-test)
    jp_line = "🇯🇵 JP = url-test"
    if jp_nodes:
        jp_line += ", " + ", ".join(jp_nodes)
    jp_line += ", url=http://www.gstatic.com/generate_204, interval=300"

    # 8) 🇺🇸 USA group (url-test)
    usa_line = "🇺🇸 USA = url-test"
    if usa_nodes:
        usa_line += ", " + ", ".join(usa_nodes)
    usa_line += ", url=http://www.gstatic.com/generate_204, interval=300"

    lines = [
        "[Proxy Group]",
        proxy_group_line,
        auto_group_line,
        ai_group_line,
        hk_line,
        sgp_line,
        tw_line,
        jp_line,
        usa_line,
        ""  # Empty line at end
    ]
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python diy.py <your-surge-config-file>")
        sys.exit(1)

    conf_path = sys.argv[1]
    if not os.path.exists(conf_path):
        print(f"File not found: {conf_path}")
        sys.exit(1)

    print(f"Parsing file: {conf_path}")
    proxy_lines = parse_surge_conf(conf_path)
    print(f"Found {len(proxy_lines)} nodes in [Proxy] section")

    if not proxy_lines:
        print("[Warning] No [Proxy] section found or section is empty.")
        sys.exit(0)

    # Analyze and classify
    classified = classify_proxies(proxy_lines)

    # Output statistics
    print("=== Statistics ===")
    print(f"ALL: {len(classified['ALL'])} nodes")
    print(f"HK: {len(classified['HK'])} nodes")
    print(f"SGP: {len(classified['SGP'])} nodes")
    print(f"TW: {len(classified['TW'])} nodes")
    print(f"JP: {len(classified['JP'])} nodes")
    print(f"USA: {len(classified['USA'])} nodes")

    # Generate [Proxy Group] text
    groups_text = generate_proxy_group_text(classified)

    # Generate diy.conf
    out_dir = os.path.dirname(conf_path)
    diy_path = os.path.join(out_dir, "diy.conf")
    with open(diy_path, 'w', encoding='utf-8') as f:
        f.write(groups_text)

    print(f"\nCustom policy groups generated to: {diy_path}\n")


if __name__ == "__main__":
    main()