#!/usr/bin/env python3
"""
简单检查并美化 bible_cho_yao_v1.5.json 的脚本
用法:
  python3 validate_bible_cho_yao.py bible_cho_yao_v1.5.json
会输出:
  - 是否为合法 JSON
  - 章节数、场景数等摘要
  - 唯一性检测（id 重复）
  - 简单风格问题警告（文件名空格、占位邮箱、anti_abuse pattern 类型为自然语言）
  - 将美化后的 JSON 写出到 bible_cho_yao_v1.5.cleaned.json
"""
import sys
import json
from collections import Counter

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(obj, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def check_unique_ids(items, key='id'):
    ids = [it.get(key) for it in items if isinstance(it, dict) and key in it]
    c = Counter(ids)
    dup = [k for k,v in c.items() if v>1]
    return dup

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_bible_cho_yao.py bible_cho_yao_v1.5.json")
        sys.exit(1)
    path = sys.argv[1]
    try:
        data = load_json(path)
    except Exception as e:
        print("JSON 解析失败:", e)
        sys.exit(2)
    print("✅ JSON 解析成功。")
    # 摘要
    chapters = data.get('selection',{}).get('chapters',[])
    scenarios = data.get('scenarios',[])
    print(f"章节数: {len(chapters)}，场景数: {len(scenarios)}")
    # 唯一性检测
    dup_ch = check_unique_ids(chapters)
    dup_sc = check_unique_ids(scenarios)
    if dup_ch:
        print("⚠️ selection.chapters 有重复 id:", dup_ch)
    else:
        print("✔ selection.chapters id 唯一")
    if dup_sc:
        print("⚠️ scenarios 有重复 id:", dup_sc)
    else:
        print("✔ scenarios id 唯一")
    # 检查 maintainer contact 占位
    maint = data.get('meta',{}).get('maintainer',{})
    contact = maint.get('contact','')
    if 'example.org' in contact or 'replace' in contact or contact.strip()=='':
        print("⚠️ maintainer.contact 似乎是占位，请替换为真实联系方式或删除。 当前:", contact)
    else:
        print("✔ maintainer.contact 已设置为:", contact)
    # 检查 docs 路径中是否有空格
    docs = data.get('docs',{})
    doc_issues = []
    for k,v in docs.items():
        if isinstance(v,str) and ' ' in v:
            doc_issues.append((k,v))
    if doc_issues:
        print("⚠️ docs 字段中存在包含空格的路径（建议去掉空格）:")
        for k,v in doc_issues:
            print("  ",k,":",v)
    else:
        print("✔ docs 字段路径看起来没有空格问题")
    # anti_abuse pattern 类型检测
    anti = data.get('safeguards',{}).get('anti_abuse',[])
    nl_patterns = []
    for a in anti:
        p = a.get('pattern','')
        if isinstance(p,str) and len(p.split())>4:
            nl_patterns.append((a.get('id'), p))
    if nl_patterns:
        print("⚠️ anti_abuse.pattern 多为自然语言描述（建议转成可执行规则，如 keywords/regex）:")
        for i,p in nl_patterns:
            print("   ",i,":",p)
    else:
        print("✔ anti_abuse.pattern 看起来简洁（或已为关键词/regex）")
    # 输出美化文件
    out = path.replace('.json','') + '.cleaned.json'
    write_json(data, out)
    print("✅ 已写出美化文件到:", out)
    print("下一步建议：")
    print("  1) 若要自动检测 anti_abuse，考虑改成 {'type':'keyword','keywords':[...]} 或 {'type':'regex','expr':'...'}")
    print("  2) 考虑生成 JSON Schema，用于 CI 校验（我可以帮你生成）")
    print("  3) 若想部署成简单网页或 API，我可以给出最小可运行示例（Node 或 Python）")

if __name__ == '__main__':
    main()