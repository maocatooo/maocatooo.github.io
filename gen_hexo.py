import os
import re

exclude = ["hexo", "node_modules", "_book"]

root = os.getcwd()
gen_dir_list = os.listdir(root)
hexo_root = os.path.join(root, "hexo", "blog", "source", "_posts")
hexo_asset_root = os.path.join(root, "hexo", "blog", "source", "asset")


def remove_exclude(dir_list):
    n_list = []
    for item in dir_list:
        path = os.path.join(root, item)
        if not os.path.isdir(path):
            pass
        elif item in exclude:
            pass
        elif "." == item[0]:
            pass
        else:
            n_list.append(item)
    return n_list


gen_dir_list = remove_exclude(gen_dir_list)


def gen_hexo(cur, dirs):
    for dir in dirs:
        path = os.path.join(cur, dir)
        if os.path.isdir(path):
            gen_hexo(path, os.listdir(path))
        else:
            if path.endswith(".md"):
                copy_md(path)
            elif "images" in path:
                copy_images(path)


def copy_md(src):
    relpath = os.path.relpath(src, root)
    target = os.path.join(hexo_root, relpath)
    dirname = os.path.dirname(target)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    base = "/".join(os.path.split(relpath)[:-1])
    with open(src, "r", encoding="utf-8") as source_file:
        with open(target, "w", encoding="utf-8") as target_file:
            for line in source_file.readlines():
                target_file.write(replace_link(line, base))


def replace_link(src, base):
    c = re.compile(r"!\[.*?\]\(.*?\)")
    if c.search(src):
        return src.replace("./images", "/asset/" + base + "/images")
    return src


def copy_images(src):
    target = os.path.join(hexo_asset_root, os.path.relpath(src, root))
    dirname = os.path.dirname(target)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(src, "rb") as source_file:
        with open(target, "wb") as target_file:
            target_file.write(source_file.read())


def clean_hexo():
    import shutil
    shutil.rmtree(hexo_root)
    shutil.rmtree(hexo_asset_root)


clean_hexo()
gen_hexo(root, gen_dir_list)
