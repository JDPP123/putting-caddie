import streamlit as st
from PIL import Image, ImageDraw

def draw_dashed_line(draw, pt1, pt2, fill, width, dash_len=15):
    """PIL에서 점선을 그리기 위한 함수"""
    x1, y1 = pt1
    x2, y2 = pt2
    for x in range(int(x1), int(x2), dash_len * 2):
        draw.line([(x, y1), (x + dash_len, y1)], fill=fill, width=width)

def main():
    st.set_page_config(page_title="스크린 퍼팅 캐디", layout="centered")
    
    st.title("⛳ 스크린 퍼팅 캐디")
    st.markdown("스크린 골프 실전용 완벽 에이밍 계산기")

    # UI 입력부 (2단으로 깔끔하게 배치)
    col1, col2 = st.columns(2)
    with col1:
        target_dir = st.radio("방향", ["L (좌측)", "R (우측)"], horizontal=True)
        target_dir = "L" if "L" in target_dir else "R"
        cups = st.number_input("컵/클럽 수", value=1.0, step=0.5)
        unit_var = st.radio("단위", ["컵", "클럽"], horizontal=True)
        
    with col2:
        dist = st.number_input("남은거리 (m)", value=5.0, step=0.5)
        height = st.number_input("높낮이 (m)", value=0.0, step=0.05)

    if st.button("계산 및 공 위치 확인", use_container_width=True):
        if dist <= 0:
            st.error("거리는 0보다 커야 합니다.")
            return
            
        cups_calc = cups * 6.0 if unit_var == "클럽" else cups
        target_dist = dist + (height * 10)
        req_deg = cups_calc * (10 / dist)

        front_map = {
            2: ("타겟방향 검은선 1/3 걸치기", "close_target"),
            4: ("타겟방향 검은선에 딱 붙이기", "edge_target"),
            5: ("녹색 매트 정중앙", "center"),
            6: ("반대방향 검은선에 딱 붙이기", "edge_opp"),
            8: ("반대방향 검은선 1/3 걸치기", "close_opp"),
            10: ("반대방향 검은선 절반 걸치기", "half_opp")
        }
        back_map = {k/2: v for k, v in front_map.items()}

        def find_closest(m, t):
            c = min(m.keys(), key=lambda k: abs(k-t))
            return c, m[c]

        f_deg, f_val = find_closest(front_map, req_deg)
        b_deg, b_val = find_closest(back_map, req_deg)

        if req_deg > 10.5:
            st.error("⚠️ 각도가 너무 큽니다. 타겟을 변경하세요.")
            return

        SW = 152  
        C_W = 760 
        C_H = 2000 
        CX = 380 
        screen_end_y = 130   
        mat_start_y = 180
        
        front_ball_y = 450 
        back_ball_y = 1600 
        target_y = mat_start_y 

        if abs(b_deg - req_deg) < abs(f_deg - req_deg) and req_deg <= 5:
            row_name = "뒷줄 (공 나오는 곳)"
            desc = b_val[0]
            pos_code = b_val[1]
            ball_y = back_ball_y
        else:
            row_name = "앞줄 (러프 앞)"
            desc = f_val[0]
            pos_code = f_val[1]
            ball_y = front_ball_y

        r = 60 
        left_line = CX - 0.5 * SW
        right_line = CX + 0.5 * SW
        
        if pos_code == "center": ball_x = CX
        elif target_dir == "R":
            if pos_code == "edge_target": ball_x = right_line - r
            elif pos_code == "close_target": ball_x = right_line - (r / 3) 
            elif pos_code == "edge_opp": ball_x = left_line + r
            elif pos_code == "close_opp": ball_x = left_line + (r / 3)   
            elif pos_code == "half_opp": ball_x = left_line                
        else: 
            if pos_code == "edge_target": ball_x = left_line + r
            elif pos_code == "close_target": ball_x = left_line + (r / 3)   
            elif pos_code == "edge_opp": ball_x = right_line - r
            elif pos_code == "close_opp": ball_x = right_line - (r / 3)  
            elif pos_code == "half_opp": ball_x = right_line  

        # 이미지 그리기 (Pillow 라이브러리 사용)
        img = Image.new('RGB', (C_W, C_H), color='#527926')
        draw = ImageDraw.Draw(img)

        # 스크린 및 벽
        draw.rectangle([0, 0, C_W, screen_end_y], fill='#1A1A1A')
        screen_poly = [(-400, 10), (C_W + 400, 10), (C_W - 20, screen_end_y), (20, screen_end_y)]
        draw.polygon(screen_poly, fill='#B0E0E6')
        draw.line([(-400, 10), (C_W - 20, screen_end_y)], fill='white', width=4)
        draw.line([(C_W + 400, 10), (20, screen_end_y)], fill='white', width=4)
        draw.rectangle([0, screen_end_y, C_W, mat_start_y], fill='#333333')

        # 매트 까만 줄
        left_b_x1_1 = CX - 1.5 * SW
        left_b_x2_1 = CX - 0.5 * SW
        right_b_x1_1 = CX + 0.5 * SW
        right_b_x2_1 = CX + 1.5 * SW
        draw.rectangle([left_b_x1_1, mat_start_y, left_b_x2_1, C_H], fill='#1A1A1A')
        draw.rectangle([right_b_x1_1, mat_start_y, right_b_x2_1, C_H], fill='#1A1A1A')

        # 가이드 점선
        front_y = 450 
        back_y = 1600
        draw_dashed_line(draw, (0, front_y), (C_W, front_y), fill="white", width=4, dash_len=15)
        draw_dashed_line(draw, (0, back_y), (C_W, back_y), fill="white", width=4, dash_len=15)

        # 에이밍 선 (빨간색)
        target_x = right_line if target_dir == "R" else left_line
        draw.line([ball_x, ball_y, target_x, target_y], fill='red', width=7)

        # 공 (흰색)
        draw.ellipse([ball_x - r, ball_y - r, ball_x + r, ball_y + r], fill='white', outline='gray', width=2)

        # 화면 출력
        st.success(f"📍 **위치:** {row_name} \n\n⛳ **세팅:** {desc} \n\n🎯 **쳐야할 거리:** {target_dist:.1f} m")
        st.image(img, use_container_width=True)

if __name__ == "__main__":
    main()
