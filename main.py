from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import random
import json
import os
from PIL import Image, ImageDraw, ImageFont
import requests
from datetime import datetime
import tempfile



@register("今日运势", "ominus", "一个今日运势海报生成图","1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)


    @filter.command("jrys")
    async def jrys(self, event:AstrMessageEvent):
        """
        处理 jrys 指令
        输入/jrys 指令后，生成今日运势海报
        """
        user_id = event.get_sender_id()
        # 获取用户头像
        avatar_path = get_avatar_img(user_id)
        if avatar_path is None:
            yield event.plain_result("获取头像失败，请稍后再试～")

        img = draw_jrys_img()
        img = draw_avatar_img(avatar_path, img) #在图片上绘制用户头像
        if img is None:
            yield event.plain_result("生成图片失败，请稍后再试～")



        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
            img = img.convert("RGB")  # 转换为 RGB 模式
            img.save(temp_file, format="JPEG", quality=85, optimize=True)
            temp_file_path = temp_file.name

        yield event.image_result(temp_file_path)

        # 用完后删除临时文件
        try:
            os.remove(temp_file_path)

        except Exception as e:
            print(f"删除临时文件失败: {e}")
            yield event.plain_result("生成图片失败，请稍后再试～")

    



#__file__是一个内置变量，它包含当前文件的相对路径。
# __file__ 变量只有在脚本文件（.py 文件）中运行时才会被定义。在交互式 Python 解释器（你通过 >>> 提示符运行代码的地方）中，__file__ 不存在。

def jrys_data_init():
    """
    初始化 jrys.json 文件
    1. 检查当前目录下是否存在 jrys.json 文件
    2. 如果不存在，则创建一个空的 jrys.json 文件
    3. 如果存在，则读取文件内容
    4. 如果文件内容不是有效的 JSON 格式，则打印错误信息
    """
    jrys_path = os.path.join(os.path.dirname(__file__), "jrys.json")
    if not os.path.exists(jrys_path):
        with open(jrys_path, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    # 读取 JSON 文件

    try:
        with open(jrys_path, 'r', encoding='utf-8') as f:
            jrys_data = json.load(f)
        
        return jrys_data
        

    except FileNotFoundError:
        print(f"文件 {jrys_path} 没找到")
    except json.JSONDecodeError:
        print(f"文件 {jrys_path} 不是有效的 JSON 格式")


# backgrounds = random.choice(os.listdir(os.path.join(os.path.dirname(__file__), "backgroundFolder"))) 这我写的有问题


def get_background_image():
    """
    随机获取背景图片
    1. 在当前目录下的 backgroundFolder 文件夹中查找所有的 txt 文件
    2. 随机选择一个 txt 文件
    3. 从选中的 txt 文件中随机选择一行
    4. 将选中的行作为图片的 URL
    5.返回图片
    """
    
    background_folder = os.path.join(os.path.dirname(__file__), "backgroundFolder")

    try:
        background_files = [f for f in os.listdir(background_folder) if os.path.splitext(f)[1] in ['.txt']]

        if background_files: #
            background = random.choice(background_files)
            backgound_file_path = os.path.join(background_folder, background)
            with open(backgound_file_path, 'r', encoding='utf-8') as f:
                background_list = f.readlines()
                image_url = random.choice(background_list).strip()

    
                image_path = os.path.join(background_folder, "images")
                if not os.path.exists(image_path):
                    os.makedirs(image_path)
                image_name = os.path.basename(image_url)
                image_path = os.path.join(image_path, image_name)
                if os.path.exists(image_path):
                    print(f"图片 {image_name} 已存在")
                    return image_path
                try:
                    response = requests.get(image_url, timeout=5)
                    response.raise_for_status()  # 检查请求是否成功

                except requests.exceptions.RequestException as e:
                    print(f"下载图片失败: {e}")
                    return None
                
                with open(image_path, 'wb') as image_file:
                    image_file.write(response.content)

                return image_path


        else:
            print("没有找到txt文件")

    except FileNotFoundError:
        print(f"文件夹 {background_folder} 没找到")

    except Exception as e:
        print(f"发送错误: {e}")





def draw_jrys_img(): 
    """
    1. 初始化 jrys.json 文件
    2. 获取当前日期
    3. 获取 jrys.json 文件中的数据
    4. 随机选择一张背景图片
    5. 在图片上绘制文字
    """
    jrys_data = jrys_data_init() #初始化数据
    if not jrys_data:
        print("没有数据")
        return
    key_list = ["84", "0", "70","28", "56", "42", "98", "14"]
    try:
        key_1 = random.choice(key_list)
        key_2 = random.choice(list(range(len(jrys_data[key_1]))))
    except IndexError:
        print("没有数据")
        return
    #获取当前日期
    date = f"{datetime.now().year}/{datetime.now().month}/{datetime.now().day}"
    fortune_summary =jrys_data[key_1][key_2]['fortuneSummary']
    lucky_star = jrys_data[key_1][key_2]['luckyStar']
    sign_text = jrys_data[key_1][key_2]['signText']
    unsign_text = jrys_data[key_1][key_2]['unsignText']
    warning_text = "仅供娱乐 | 相信科学 | 请勿迷信"

    #如果unsign_lines>3行，怕这个warning_text和unsign_text贴在一起，加个自动换行的
    unsign_lines = wrap_text(unsign_text, max_width=1000)
    warning_text_y = 1850
    unsign_text_y = 1700
    #如果unsign_lines>3行，warning_text_y向下移动 unsign_text_y向上移动
    if len(unsign_lines) > 3:
        warning_text_y += (len(unsign_lines) - 3) * 10 #每行10像素的间距
        unsign_text_y -= (len(unsign_lines) - 3) * 15 #每行15像素的间距

        



    image_path = get_background_image()
    #裁切图片，并且添加透明图层
    image = add_transparent_layer(crop_center(image_path), position=(0,1270), box_width=1080, box_height=700)

    #在图片上绘制文字
    image = draw_text(image, text=date, position='center',y=1300, color=(255, 255, 255), font_size=50, gradients=True)
    image = draw_text(image, text=fortune_summary, position='center',y=1400, color=(255, 255, 255), font_size=60)
    image = draw_text(image, text=lucky_star, position='center',y=1500, color=(255, 255, 255), font_size=60, gradients=True)
    image = draw_text(image, text=sign_text, position='left', y=1600, color=(255, 255, 255), font_size=30)
    image = draw_text(image, text=unsign_text, position='left', y=unsign_text_y, color=(255, 255, 255), font_size=30)
    image = draw_text(image, text=warning_text, position='center', y=warning_text_y, color=(255, 255, 255), font_size=30)
            
    return image






def draw_text(img, text, position, y=None, color=(255, 255, 255),font_size=36, max_width=800, gradients=False):
    """
    在图片上绘制文字
    参数：
        img (Image): 要绘制的图片
        text (str): 要绘制的文字
        position (tuple or str): 文字的位置, 可为'topleft','center'或坐标元组
        y (int): 文字的y坐标,如果position为'topleft'或'center',则y无效
        color (tuple): 文字颜色，默认为白色
        font_size (int): 字体大小,默认为36
        max_width (int): 文字的最大宽度,默认为800
        gradients (bool): 是否使用渐变色填充文字，默认为False
    """
    draw = ImageDraw.Draw(img)

     #字体
    try:
        font_path = os.path.join(os.path.dirname(__file__), 'font', '千图马克手写体.ttf')

        font = ImageFont.truetype(font_path, font_size) #加载字体，字号36

    except FileNotFoundError:
            print(f"无法找到字体文件 {font_path},以切换默认字体")
            font = ImageFont.load_default() #找不到就用默认字体

    # 自动换行处理
    lines = wrap_text(text=text, font=font, max_width=1000, draw=draw) #将文字按最大宽度进行换行

    #获取图片的宽高
    img_width, img_height = img.size

    if isinstance(position, str):
        if position == 'center':  
            #计算文字的位置
            x_func = lambda line: (img_width - draw.textbbox((0, 0), line, font=font)[2]) // 2
        
        elif position == 'left':
            x_func = lambda line: 20
        else:
            raise ValueError("position参数错误,只能为'topleft','center'或坐标元组")
        #计算y坐标
        text_y = y if y is not None else 0
    elif isinstance(position, tuple):
        text_x, text_y = position
        x_func = lambda line: text_x
    else:
        raise ValueError("position参数错误,只能为'topleft','center'或坐标元组")
        
    # 绘制每一行
    line_spacing = int(font_size * 1.5) # 行间距
    for line in lines:
        if gradients:
            text_x = x_func(line)
            for char in line:
                #
                colors = get_light_color()
                gradient_char = create_gradients_image(char, font, colors)
                img.paste(gradient_char, (text_x, text_y), gradient_char)
                text_x += font.getbbox(char)[2] # 更新x坐标
        else:

            draw.text((x_func(line), text_y), line, font=font, fill=color)

        text_y += line_spacing # 更新y坐标
        
       
    
    return img

    
        



def crop_center(image_path: str, width=1080, height=1920):

    """
    从图片中间裁剪指定尺寸的区域，如果图片尺寸小于目标尺寸，则先放大,太大则缩小。

    参数：

        width (int): 裁剪宽度，默认为 1080 像素。
        height (int): 裁剪高度，默认为 1920 像素。
    """
    try:
        img = Image.open(image_path).convert("RGBA")
        img_width, img_height = img.size

        # 如果图片尺寸小于目标尺寸，则先放大
        if img_width < width or img_height < height:
            scale_x = width / img_width
            scale_y = height / img_height
            scale = max(scale_x, scale_y)# 保持比例，选择较大的缩放倍数
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img = img.resize((new_width, new_height), Image.LANCZOS) #
        
        #如果图片尺寸远大于目标尺寸

        else:
            max_scale = 1.8 #防止图片太大浪费资源
            if img_width > width * max_scale or img_width > height * max_scale:
                scale_x = (width * max_scale) / img_width
                scale_y = (height * max_scale) / img_height
                scale = min(scale_x, scale_y)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                img = img.resize((new_width, new_height), Image.LANCZOS)


               

        #重新获取放大后的图片尺寸
        img_width, img_height = img.size


        left = (img_width - width) / 2
        top = (img_height - height) / 2
        right = (img_width + width) / 2
        bottom = (img_height + height) / 2

        # 创建半透明图层

        cropped_img = img.crop((left, top, right, bottom))



        return cropped_img
    
    except FileNotFoundError:
         print(f"错误：找不到图片文件：{image_path}")
    except Exception as e:
        print(f"发生错误：{e}")




def add_transparent_layer(
    base_img,
    box_width=800, 
    box_height=400,
    position=(100, 200),
    layer_color=(0, 0, 0, 128),
    radius=50,
    ) -> Image:

    """
    在图片上添加一个半透明图层

    参数：
        base_img (Image): 背景图像（RGBA 格式）
        text (str): 要绘制的文字内容
        box_width (int): 半透明框的宽度
        box_height (int): 半透明框的高度
        position (tuple): 半透明框的位置
        layer_color (tuple): 半透明层颜色，RGBA 格式
        radius (int): 圆角半径
    返回：
        合成后的 Image 对象
    """
    x1, y1 = position
    x2 = x1 + box_width
    y2 = y1 + box_height
 
    #创建半透明图层
    overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    draw.rounded_rectangle((x1,y1,x2,y2), radius=radius, fill=layer_color)

    return Image.alpha_composite(base_img, overlay)


def wrap_text(text: str, draw=None,max_width=1000, font=None):
    """
     将文字按最大宽度进行换行
    参数：
        text (str): 原始文字
        max_width (int): 最大宽度   
        draw: ImageDraw对象，用于测量文字宽度
        font: ImageFont对象默认1000
    返回：
        list[str]: 每行一段文字

    """

    if draw is None:
        img = Image.new('RGB', (1080, 1920))
        draw = ImageDraw.Draw(img)

    if font is None:
        #字体
        try:
            font_path = os.path.join(os.path.dirname(__file__), 'font', '千图马克手写体.ttf')

            font = ImageFont.truetype(font_path, 36) #加载字体，字号36

        except FileNotFoundError:
                print(f"无法找到字体文件 {font_path},以切换默认字体")
                font = ImageFont.load_default() #找不到就用默认字体

          

    lines = []
    line = ""
    for char in text:
        test_line = line + char
        width = draw.textbbox((0, 0), test_line, font=font)[2]
        if width <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = char
    if line:
        lines.append(line)
    return lines



def create_gradients_image(char, font, colors):
    """
    创建渐变色字体图像
    参数：
        char (str): 要绘制的字符
        font: ImageFont对象
        colors (list of tuple): 渐变色列表，包含起始和结束颜色

    """
    width, height = font.getbbox(char)[2:]
    gradient = Image.new("RGBA", (width, height), color=0)
    draw = ImageDraw.Draw(gradient)

    #字体蒙版
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((0, 0), char, font=font, fill=255)

    num_colors = len(colors)
    if num_colors < 2:
        raise ValueError("至少需要两个颜色进行渐变")
    

    #绘制横向多颜色渐变色条
    segement_width = width / (num_colors - 1)  # 每个颜色段的宽度
    for i in range (num_colors - 1):
        start_color = colors[i]
        end_color = colors[i + 1]
        start_x = int(i * segement_width)
        end_x = int((i + 1) * segement_width)

        for x in range(start_x, end_x):
            factor = (x - start_x) / segement_width
            color = tuple([
                int(start_color[j] + (end_color[j] - start_color[j]) * factor)
                for j in range(3)
            ])
            draw.line([(x, 0), (x, height)], fill=color)
    
    gradient.putalpha(mask)  # 添加蒙版
    
    return gradient


def get_light_color():
    

    light_colors = [
        (255, 250, 205),  # 浅黄色
        (173, 216, 230),  # 浅蓝色
        (221, 160, 221),  # 浅紫色
        (255, 182, 193),  # 浅粉色
        (240, 230, 140),  # 浅卡其色
        (224, 255, 255),  # 浅青色
        (245, 245, 220),  # 浅米色
        (230, 230, 250),  # 浅薰衣草色
    ]
    return random.choices(light_colors, k=4) #随机选4个颜色进行渐变



def get_avatar_img(user_id: str) -> str:
    """
    获取用户头像
    1. 获取用户头像
    2. 获取用户头像的 URL
    3. 下载头像
    4. 返回头像的路径
    """
    url = f"http://q.qlogo.cn/g?b=qq&nk={user_id}&s=640"
    response = requests.get(url)
    if response.status_code == 200:
        avatar_folder = os.path.join(os.path.dirname(__file__), "avatars")
        if not os.path.exists(avatar_folder):
            os.makedirs(avatar_folder)


        with open(os.path.join(avatar_folder, f"{user_id}.jpg"), 'wb') as f:
            f.write(response.content)
        
        return os.path.join(avatar_folder, f"{user_id}.jpg")
    

def draw_avatar_img(avatar_path: str, img: Image) -> Image:
    """
    在图片上绘制用户头像
    1. 获取用户头像
    2. 将头像裁剪为圆形
    3. 将头像绘制到图片上
    """
    avatar = Image.open(avatar_path).convert("RGBA")
    avatar = avatar.resize((150, 150), Image.LANCZOS)

    # 创建一个与头像尺寸相同的透明蒙版
    mask = Image.new("L", avatar.size, 0)
    draw = ImageDraw.Draw(mask)

    #绘制一个白色的圆形，作为不透明区域
    draw.ellipse((0, 0, avatar.size[0], avatar.size[1]), fill=255)

    # 将蒙版应用到头像上
    avatar.putalpha(mask)

    # 将头像粘贴到图片上
    img.paste(avatar, (60, 1350), avatar)



    return img




if __name__ == "__main__":

    draw_jrys_img()







    













        

        










