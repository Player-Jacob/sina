import json

import jieba
import stylecloud
import numpy as np
from PIL import Image
from snownlp import SnowNLP
from wordcloud import WordCloud, ImageColorGenerator, STOPWORDS
import matplotlib.pyplot as plt


def get_data_from_json():
    """
    从JSON文件中读取数据
    """
    with open('weibo.json', 'r') as f:
        for item in f.readlines():
            yield json.loads(item)


def get_data():
    content_list = []
    for item in get_data_from_json():
        content_list.append(item.get('content', ''))
    wordlist = jieba.lcut(''.join(content_list))  # 切割词语
    return ' '.join([item for item in wordlist if len(item) >= 2])  # 空格链接词语


def generate_word_cloud():
    space_list = get_data()
    back_ground = np.array(Image.open('img.png'))

    # wc = WordCloud(width=1400, height=2200,
    #                background_color='white',
    #                mode='RGB',
    #                mask=back_ground,  # 添加蒙版，生成指定形状的词云，并且词云图的颜色可从蒙版里提取
    #                max_words=500,
    #                stopwords=STOPWORDS.add('老年人'),  # 内置的屏蔽词,并添加自己设置的词语
    #                font_path='AaBanRuoKaiShu-2.ttf',
    #                max_font_size=150,
    #                relative_scaling=0.6,  # 设置字体大小与词频的关联程度为0.4
    #                random_state=50,
    #                scale=2
    #                ).generate(space_list)
    # image_color = ImageColorGenerator(back_ground)  # 设置生成词云的颜色，如去掉这两行则字体为默认颜色
    # wc.recolor(color_func=image_color)
    #
    # plt.imshow(wc)  # 显示词云
    # plt.axis('off')  # 关闭x,y轴
    # plt.show()  # 显示
    # wc.to_file('test1_ciyun.jpg')  # 保存词云图

    stylecloud.gen_stylecloud(
        text=space_list,  # 上面分词的结果作为文本传给text参数
        size=512,
        font_path='msyh.ttc',  # 字体设置
        palette='cartocolors.qualitative.Pastel_7',  # 调色方案选取，从palettable里选择
        gradient='horizontal',  # 渐变色方向选了垂直方向
        icon_name='fab fa-weixin',  # 蒙版选取，从Font Awesome里选
        output_name='test_ciyun.png')  # 输出词云图


def emotion_analysis():
    text_list = []
    for li in get_data():
        if len(li) != 0:
            s = SnowNLP(li)
            text_list.append(s.sentiments)
    plt.hist(text_list, bins=np.arange(0, 1, 0.02))
    plt.show()


if __name__ == '__main__':
    emotion_analysis()