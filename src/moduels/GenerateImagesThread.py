from PySide6.QtCore import *
from PIL import Image
from handright import Template, handwrite, LayoutError

class GenerateImagesThread(QThread):
    text = None
    template = None
    outputPath = None
    signal = Signal(str)
    showImage = False
    bgWidth = None
    bgHeight = None
    fontSize = None
    leftMargin = None
    rightMargin = None
    topMargin = None
    bottomMargin = None
    lineSpacing = None

    def __init__(self, parent=None):
        super(GenerateImagesThread, self).__init__(parent)

    def print(self, text):
        self.signal.emit(text)

    def run(self):
        self.signal.emit('开始生成图片\n\n')
        try:
            images = handwrite(self.text, self.template)
            for i, im in enumerate(images):
                assert isinstance(im, Image.Image)
                self.signal.emit('第 %s 张图片生成\n\n' % str(int(i) + 1))
                if self.showImage == True:
                    im.show()
                outputDir = self.outputPath.replace('\\', '/')
                im.save(outputDir + "/{}.webp".replace('//', '/').format(i))
            self.signal.emit('所有图片生成完毕，输出文件夹为：%s\n\n' % outputDir)
        except LayoutError as e:
            self.signal.emit('布局参数错误：\n\n')
            self.signal.emit(str(e) + '\n\n')
            msg = str(e)
            if 'width < left_margin + font.size + right_margin' in msg:
                need = (self.leftMargin or 0) + (self.fontSize or 0) + (self.rightMargin or 0)
                self.signal.emit(
                    f'背景宽度：{self.bgWidth or "?"}  '
                    f'左边距：{self.leftMargin or "?"}  '
                    f'字号：{self.fontSize or "?"}  '
                    f'右边距：{self.rightMargin or "?"}\n'
                    f'至少需要宽度：{need}\n'
                    f'请增大背景宽度，或减小边距/字号。\n\n'
                )
            elif 'height < top_margin + line_spacing + bottom_margin' in msg:
                need = (self.topMargin or 0) + (self.lineSpacing or 0) + (self.bottomMargin or 0)
                self.signal.emit(
                    f'背景高度：{self.bgHeight or "?"}  '
                    f'上边距：{self.topMargin or "?"}  '
                    f'行间距：{self.lineSpacing or "?"}  '
                    f'下边距：{self.bottomMargin or "?"}\n'
                    f'至少需要高度：{need}\n'
                    f'请增大背景高度，或减小边距/行间距。\n\n'
                )
            elif 'font.size > line_spacing' in msg:
                self.signal.emit(
                    f'字号：{self.fontSize or "?"}  '
                    f'行间距：{self.lineSpacing or "?"}\n'
                    f'行间距必须 ≥ 字号，请增大行间距或减小字号。\n\n'
                )
        except Exception as e:
            self.signal.emit('出错了，报错信息如下：\n\n')
            self.signal.emit(str(e) + '\n\n')
