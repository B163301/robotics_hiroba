import argparse
import os


def get_args():
    parser = argparse.ArgumentParser(description='画像ビューア生成')
    parser.add_argument('--inf', type=str, default='../data/list_savedphoto.txt',
                        help='保存済み画像ファイル名一覧')
    parser.add_argument('--tmpf', type=str, default='../src/tmp_img_viewer.txt',
                        help='ビューアのテンプレート')
    parser.add_argument('--outf', type=str, default='../src/interface/img_viewer.html',
                        help='画像ビューアhtmlファイル')
    parser.add_argument('--outdir', type=str, default='./photo/',
                        help='画像ビューアhtmlファイル')
    return parser.parse_args()


def load_lines(filename):
    with open(filename, 'r') as f:
        lines = f.read().split('\n')[:-1]
    return lines


def load(filename):
    with open(filename, 'r') as f:
        s = f.read()
    return s


def save(filename, data):
    with open(filename, 'w') as f:
        f.write(data)


def make_img_viewer_html(inf, tmpf, outf, outdir):
    # 保存済み画像ファイル名一覧を読み込み
    fnames = load_lines(inf)
    # 画像ビューアhtmlファイルを生成
    tmp = load(tmpf)
    tmp_img = '<div class="viewer_photo">\n'
    tmp_img += '<p>{title}</p>\n'
    tmp_img += '<img src="{img_src}" alt="{img_alt}" title="{img_title}" width=400>\n'
    tmp_img += '</div>'
    imglist = ''
    for fname in fnames:
        fname = outdir + os.path.basename(fname)
        title = '{}年{}月{}日{}時{}分{}秒'.format(
            fname[-19:-15], fname[-15:-13], fname[-13:-11],
            fname[-11:-9], fname[-9:-7], fname[-7:-5])
        imglist += tmp_img.format(
            title=title,
            img_src=fname,
            img_alt=title,
            img_title=title)
    tmp = tmp.format(imglist)
    save(outf, tmp)


if __name__ == '__main__':
    args = get_args()
    make_img_viewer_html(args.inf, args.tmpf, args.outf, args.outdir)
