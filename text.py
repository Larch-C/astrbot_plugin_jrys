from PIL import Image, ImageDraw, ImageFont
import os
import random
import math

def create_gradient_char(char, font, start_color, end_color):
    """
    创建一个渐变填充的单字符图片
    """
    width, height = font.getbbox(char)[2:]
    gradient = Image.new("RGBA", (width, height), color=0)
    draw = ImageDraw.Draw(gradient)

    # 字体蒙版
    mask = Image.new("L", (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.text((0, 0), char, font=font, fill=255)

    # 绘制横向渐变色条
    for x in range(width):
        factor = x / width
        color = tuple([
            int(start_color[i] + (end_color[i] - start_color[i]) * factor)
            for i in range(3)
        ])
        draw.line([(x, 0), (x, height)], fill=color)

    gradient.putalpha(mask)
    return gradient

def get_random_light_color():
    """
    生成一个随机的浅色
    """
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
    return random.choice(light_colors)

def draw_gradient_char_text(img, text, position='center', y=0, font_size=60):
    """
    在图片上绘制每个字都是不同浅色+内部渐变的文字
    """
    draw = ImageDraw.Draw(img)

    # 加载字体
    try:
        font_path = os.path.join(os.path.dirname(__file__), 'font', '千图马克手写体.ttf')
        font = ImageFont.truetype(font_path, font_size)
    except:
        font = ImageFont.load_default()

    # 计算总宽度
    total_width = sum(font.getbbox(c)[2] for c in text)

    if isinstance(position, str):
        img_width, _ = img.size
        if position == 'center':
            x = (img_width - total_width) // 2
        elif position == 'left':
            x = 20
        else:
            raise ValueError("position 参数错误")
    elif isinstance(position, tuple):
        x, y = position
    else:
        raise ValueError("position 参数错误")

    for char in text:
        # 每个字符使用不同的浅色渐变起始和结束值
        start_color = get_random_light_color()
        end_color = get_random_light_color()
        char_img = create_gradient_char(char, font, start_color, end_color)
        img.paste(char_img, (x, y), char_img)
        x += font.getbbox(char)[2]

    return img

def draw_dashed_line(draw, start, end, dash_length, gap_length, color):
    """绘制虚线"""
    x1, y1 = start
    x2, y2 = end
    
    # 计算线段总长度和角度
    line_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    angle = math.atan2(y2 - y1, x2 - x1)
    
    # 计算x和y方向上的增量
    dx = math.cos(angle)
    dy = math.sin(angle)
    
    # 绘制虚线
    current_length = 0
    drawing = True  # 开始是绘制状态
    
    while current_length < line_length:
        segment_length = min(dash_length if drawing else gap_length, line_length - current_length)
        
        if drawing:
            segment_end_x = x1 + dx * (current_length + segment_length)
            segment_end_y = y1 + dy * (current_length + segment_length)
            draw.line([(x1 + dx * current_length, y1 + dy * current_length), 
                      (segment_end_x, segment_end_y)], fill=color, width=2)
        
        current_length += segment_length
        drawing = not drawing

def draw_dashed_arc(draw, center, radius, start_angle, end_angle, dash_length, gap_length, color):
    """绘制虚线圆弧"""
    # 转换为弧度
    start_rad = math.radians(start_angle)
    end_rad = math.radians(end_angle)
    
    # 计算弧长
    arc_length = radius * abs(end_rad - start_rad)
    
    # 计算弧上的点数
    num_segments = int(arc_length / (dash_length + gap_length)) + 1
    
    if num_segments <= 1:
        # 如果只有一段，直接画一个完整的弧
        total_angle = end_rad - start_rad
        segment_angle = total_angle / 2
        mid_angle = start_rad + segment_angle
        
        x = center[0] + radius * math.cos(mid_angle)
        y = center[1] + radius * math.sin(mid_angle)
        
        draw.arc([center[0] - radius, center[1] - radius, 
                  center[0] + radius, center[1] + radius], 
                 start_angle, end_angle, fill=color, width=2)
    else:
        # 计算每段弧对应的角度
        angle_per_segment = (end_rad - start_rad) / num_segments
        
        for i in range(num_segments):
            segment_start = start_rad + i * angle_per_segment
            segment_end = segment_start + angle_per_segment * dash_length / (dash_length + gap_length)
            
            if segment_end > end_rad:
                segment_end = end_rad
                
            # 转换回角度
            start_deg = math.degrees(segment_start)
            end_deg = math.degrees(segment_end)
            
            draw.arc([center[0] - radius, center[1] - radius, 
                      center[0] + radius, center[1] + radius], 
                     start_deg, end_deg, fill=color, width=2)

def draw_dashed_rounded_rectangle(img, position, size, radius=20, dash_length=10, gap_length=5, color=(255, 255, 255, 180)):
    """
    在图片上绘制灰色虚线圆角方框
    
    参数:
    img - PIL Image对象
    position - 左上角坐标元组 (x, y)
    size - 方框尺寸元组 (width, height)
    radius - 圆角半径
    dash_length - 虚线段长度
    gap_length - 虚线间隔长度
    color - 线条颜色，默认半透明白色
    """
    # 创建一个透明的图层用于绘制
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    x, y = position
    width, height = size
    
    # 定义四个角的坐标
    tl = (x, y)  # 左上
    tr = (x + width, y)  # 右上
    br = (x + width, y + height)  # 右下
    bl = (x, y + height)  # 左下
    
    # 画虚线圆角矩形
    # 上边
    draw_dashed_line(draw, (tl[0] + radius, tl[1]), (tr[0] - radius, tr[1]), dash_length, gap_length, color)
    # 右边
    draw_dashed_line(draw, (tr[0], tr[1] + radius), (br[0], br[1] - radius), dash_length, gap_length, color)
    # 下边
    draw_dashed_line(draw, (bl[0] + radius, bl[1]), (br[0] - radius, br[1]), dash_length, gap_length, color)
    # 左边
    draw_dashed_line(draw, (tl[0], tl[1] + radius), (bl[0], bl[1] - radius), dash_length, gap_length, color)
    
    # 画圆角
    # 左上角
    draw_dashed_arc(draw, (tl[0] + radius, tl[1] + radius), radius, 180, 270, dash_length, gap_length, color)
    # 右上角
    draw_dashed_arc(draw, (tr[0] - radius, tr[1] + radius), radius, 270, 360, dash_length, gap_length, color)
    # 右下角
    draw_dashed_arc(draw, (br[0] - radius, br[1] - radius), radius, 0, 90, dash_length, gap_length, color)
    # 左下角
    draw_dashed_arc(draw, (bl[0] + radius, bl[1] - radius), radius, 90, 180, dash_length, gap_length, color)
    
    # 将绘制的矩形叠加到原图上
    img = Image.alpha_composite(img, overlay)
    return img

# 示例使用
if __name__ == "__main__":
    # 打开背景图片
    img_path = r"D:\QQbot\AstrBot-3.4.39\AstrBot-3.4.39\data\plugins\astrbot_plugin_jrysprpr\backgroundFolder\images\0e289f2296faaacc5124964b28b18d180ab04059.jpg"
    img = Image.open(img_path).convert("RGBA")

    # 绘制灰色虚线圆角方框
    # 计算合适的方框位置和大小
    img_width, img_height = img.size
    box_width = 400
    box_height = 200
    box_x = (img_width - box_width) // 2
    box_y = 450
    
    img = draw_dashed_rounded_rectangle(img, (box_x, box_y), (box_width, box_height))

    # 绘制星星评分
    img = draw_gradient_char_text(img, "★★★★★★☆", position='center', y=500, font_size=60)

    # 显示图片
    img.show()