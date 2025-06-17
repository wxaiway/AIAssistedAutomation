from manim import *

class HanoiTower(Scene):
    def construct(self):
        # 定义颜色
        POLE_COLOR = "#A0522D"  # 柱子的颜色
        BASE_COLOR = "#8B4513"  # 底座的颜色
        
        # 设置常量
        DISKS = 4  # 圆盘数量
        TOWER_DISTANCE = 3  # 减小塔之间的距离
        POLE_WIDTH = 0.1  # 细化柱子宽度
        POLE_HEIGHT = 2  # 减小柱子高度
        DISK_HEIGHT = 0.25  # 减小圆盘高度
        BASE_HEIGHT = 0.2  # 底座高度
        BASE_WIDTH = 2  # 底座宽度

        # 用于跟踪每个塔上的圆盘
        tower_states = [[], [], []]

        # 1. 问题说明 - 调整位置到顶部
        title = Text("汉诺塔问题", font="PingFang SC", font_size=36).to_edge(UP, buff=0.2)
        self.play(Write(title))
        
        problem_text = Text(
            "规则：\n"
            "1. 一次只能移动一个圆盘\n"
            "2. 小圆盘上不能放大圆盘\n"
            "3. 要将所有圆盘从A柱移动到C柱",
            font="PingFang SC",
            font_size=24,
            line_spacing=1.2
        ).next_to(title, DOWN, buff=0.3)
        
        self.play(Write(problem_text))
        self.wait(2)
        self.play(FadeOut(problem_text))

        # 2. 创建塔座 - 添加底座
        towers = VGroup()
        bases = VGroup()
        poles = VGroup()
        
        for i in range(3):
            # 创建底座
            base = Rectangle(
                width=BASE_WIDTH,
                height=BASE_HEIGHT,
                fill_color=BASE_COLOR,
                fill_opacity=1,
                stroke_color=BASE_COLOR
            )
            
            # 创建柱子
            pole = Rectangle(
                width=POLE_WIDTH,
                height=POLE_HEIGHT,
                fill_color=POLE_COLOR,
                fill_opacity=1,
                stroke_color=POLE_COLOR
            )
            
            # 将底座和柱子组合
            base.move_to(i * TOWER_DISTANCE * RIGHT - TOWER_DISTANCE * RIGHT)
            pole.next_to(base, UP, buff=0)
            
            bases.add(base)
            poles.add(pole)
            towers.add(VGroup(base, pole))

        # 调整整个塔组的位置，使其居中且略微向下
        towers.shift(DOWN * 0.5)
        
        # 添加标签，确保在底座下方
        labels = VGroup()
        for i, label in enumerate(['A', 'B', 'C']):
            text = Text(label, font="PingFang SC", font_size=24)
            text.next_to(bases[i], DOWN, buff=0.2)
            labels.add(text)

        self.play(Create(towers), Write(labels))

        # 3. 创建圆盘 - 调整大小和颜色
        disks = []
        colors = ["#FF0000", "#FFA500", "#FFFF00", "#00FF00", "#0000FF", "#800080", "#FFC0CB"]

        
        for i in range(DISKS):
            width = BASE_WIDTH * (0.4 + (DISKS - i - 1) * 0.15)  # 减小圆盘宽度差异
            disk = Rectangle(
                width=width,
                height=DISK_HEIGHT,
                fill_color=colors[i],
                fill_opacity=1,
                stroke_width=1
            ).round_corners(0.1)  # 添加圆角
            
            # 将圆盘放置在第一根柱子上
            disk.move_to(
                towers[0].get_bottom() + 
                UP * (BASE_HEIGHT/2 + i * DISK_HEIGHT + DISK_HEIGHT/2)
            )
            disks.append(disk)
            tower_states[0].append(disk)

        # 将解法说明移到右上角，避免重叠
        solution_method = Text(
            "解法思路：\n"
            "1. 将n-1个圆盘移到B柱\n"
            "2. 将最大圆盘移到C柱\n"
            "3. 将n-1个圆盘从B移到C",
            font="PingFang SC",
            font_size=24,
            line_spacing=1.2
        ).to_corner(UR, buff=0.5)
        
        self.play(*[Create(disk) for disk in disks], Write(solution_method))
        self.wait(2)

        # 移动次数计数器 - 调整位置到左上角
        move_count = Integer(0)
        move_count_text = Text("移动次数：", font="PingFang SC", font_size=24).to_corner(UL, buff=0.5)
        move_count.next_to(move_count_text, RIGHT)
        self.play(Write(move_count_text), Write(move_count))

        # 移动函数
        def move_disk(from_tower, to_tower):
            if not tower_states[from_tower]:
                return False
                
            disk = tower_states[from_tower][-1]
            
            if tower_states[to_tower]:
                top_disk = tower_states[to_tower][-1]
                if disk.width > top_disk.width:
                    return False
            
            # 调整移动路径
            start_pos = disk.get_center()
            top_pos = poles[from_tower].get_top() + UP * DISK_HEIGHT
            target_top_pos = poles[to_tower].get_top() + UP * DISK_HEIGHT
            target_pos = towers[to_tower].get_bottom() + UP * (
                BASE_HEIGHT/2 + 
                len(tower_states[to_tower]) * DISK_HEIGHT + 
                DISK_HEIGHT/2
            )

            self.play(disk.animate.move_to(top_pos), run_time=0.2)
            self.play(disk.animate.move_to(target_top_pos), run_time=0.2)
            self.play(disk.animate.move_to(target_pos), run_time=0.2)
            
            tower_states[from_tower].pop()
            tower_states[to_tower].append(disk)
            
            move_count.increment_value()
            return True

        def hanoi(n, from_tower, aux_tower, to_tower):
            if n > 0:
                hanoi(n-1, from_tower, to_tower, aux_tower)
                move_disk(from_tower, to_tower)
                hanoi(n-1, aux_tower, from_tower, to_tower)

        # 执行移动
        hanoi(DISKS, 0, 1, 2)

        # 验证并显示结果 - 调整位置避免重叠
        if len(tower_states[2]) == DISKS and all(
            tower_states[2][i].width > tower_states[2][i+1].width 
            for i in range(len(tower_states[2])-1)
        ):
            completion_text = Text(
                "完成!", 
                font="PingFang SC", 
                color=GREEN
            ).to_edge(DOWN, buff=0.5)
        else:
            completion_text = Text(
                "移动失败!", 
                font="PingFang SC", 
                color=RED
            ).to_edge(DOWN, buff=0.5)
            
        self.play(Write(completion_text))
        self.wait(2)

        # 显示结果 - 调整位置和大小
        final_text = VGroup(
            Text(f"总共移动了 {2**DISKS - 1} 次", font="PingFang SC", font_size=24),
            Text("移动次数公式：2ⁿ - 1", font="PingFang SC", font_size=24),
            Text("n 是圆盘数量", font="PingFang SC", font_size=20)
        ).arrange(DOWN, buff=0.2).next_to(completion_text, UP, buff=0.3)
        
        self.play(Write(final_text))
        self.wait(2)

        # 结束动画
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(1)


