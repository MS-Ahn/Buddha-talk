"""
PWA 아이콘 자동 생성 스크립트
Pillow 라이브러리를 사용하여 다양한 크기의 아이콘 생성
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_buddha_icon(size):
    """부처님 아이콘 생성"""
    # 이미지 생성
    img = Image.new('RGB', (size, size), color='#D4AF37')
    draw = ImageDraw.Draw(img)

    # 스케일링 팩터
    s = size / 512

    # 후광 (배경 원)
    halo_radius = int(240 * s)
    draw.ellipse(
        [(size//2 - halo_radius, size//2 - halo_radius),
         (size//2 + halo_radius, size//2 + halo_radius)],
        fill='#FFD700',
        outline='#FFD700'
    )

    # 내부 원 (밝은 금색)
    inner_radius = int(220 * s)
    draw.ellipse(
        [(size//2 - inner_radius, size//2 - inner_radius),
         (size//2 + inner_radius, size//2 + inner_radius)],
        fill='#D4AF37'
    )

    # 얼굴
    face_y = int(220 * s)
    face_radius = int(120 * s)
    draw.ellipse(
        [(size//2 - face_radius, face_y - face_radius),
         (size//2 + face_radius, face_y + face_radius)],
        fill='#F5DEB3'
    )

    # 눈
    eye_y = int(210 * s)
    eye_radius = int(8 * s)
    left_eye_x = int(226 * s)
    right_eye_x = int(286 * s)

    draw.ellipse(
        [(left_eye_x - eye_radius, eye_y - eye_radius),
         (left_eye_x + eye_radius, eye_y + eye_radius)],
        fill='#333333'
    )
    draw.ellipse(
        [(right_eye_x - eye_radius, eye_y - eye_radius),
         (right_eye_x + eye_radius, eye_y + eye_radius)],
        fill='#333333'
    )

    # 미소 (간단한 호)
    smile_y = int(240 * s)
    smile_width = int(60 * s)
    smile_height = int(30 * s)
    draw.arc(
        [(size//2 - smile_width, smile_y - smile_height//2),
         (size//2 + smile_width, smile_y + smile_height)],
        start=0,
        end=180,
        fill='#333333',
        width=int(4 * s)
    )

    # 머리 (타원)
    head_y = int(140 * s)
    head_rx = int(100 * s)
    head_ry = int(40 * s)
    draw.ellipse(
        [(size//2 - head_rx, head_y - head_ry),
         (size//2 + head_rx, head_y + head_ry)],
        fill='#8B4513'
    )

    # 몸 (삼각형)
    body_points = [
        (size//2, int(340 * s)),
        (int(180 * s), int(460 * s)),
        (int(332 * s), int(460 * s))
    ]
    draw.polygon(body_points, fill='#FF8C00')

    # 합장한 손
    hand_y = int(380 * s)
    hand_rx = int(30 * s)
    hand_ry = int(50 * s)
    draw.ellipse(
        [(size//2 - hand_rx, hand_y - hand_ry),
         (size//2 + hand_rx, hand_y + hand_ry)],
        fill='#F5DEB3'
    )

    # 이모지 스타일 추가 (선택적)
    try:
        # 텍스트로 🙏 추가
        font_size = int(60 * s)
        text = "🙏"
        # 기본 폰트 사용 (이모지가 안 나올 수 있음)
        draw.text((size//2, int(480 * s)), text, fill='white', anchor='mm')
    except:
        pass

    return img

def main():
    """모든 크기의 아이콘 생성"""
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]

    # 아이콘 디렉토리 확인
    icon_dir = os.path.join('static', 'icons')
    os.makedirs(icon_dir, exist_ok=True)

    print("PWA 아이콘 생성 중...")

    for size in sizes:
        icon = create_buddha_icon(size)
        filename = f'icon-{size}x{size}.png'
        filepath = os.path.join(icon_dir, filename)
        icon.save(filepath, 'PNG')
        print(f"[OK] {filename} 생성 완료")

    print("\n모든 아이콘 생성 완료!")
    print(f"위치: {os.path.abspath(icon_dir)}")
    print("\n팁: 더 나은 디자인을 원하시면 Figma나 온라인 도구를 사용하세요:")
    print("   https://www.pwabuilder.com/imageGenerator")

if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print("[ERROR] Pillow 라이브러리가 필요합니다.")
        print("설치: pip install pillow")
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
