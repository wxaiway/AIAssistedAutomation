from manim import *

class HanoiTower(Scene):
    def construct(self):
        # 设置常量
        DISKS = 5  # 圆盘数量
        TOWER_DISTANCE = 4  # 塔之间的距离
        BASE_WIDTH = 1  # 底座宽度
        DISK_HEIGHT = 0.3  # 圆盘高度
        
        # 创建三个塔的底座
        towers = VGroup()
        for i in range(3):
            base = Rectangle(
                width=BASE_WIDTH,
                height=DISKS * DISK_HEIGHT * 2.5,
                fill_color=GRAY,
                fill_opacity=0.5
            ).move_to(i * TOWER_DISTANCE * RIGHT - TOWER_DISTANCE * RIGHT)
            towers.add(base)
        
        # 创建圆盘，使用预定义的颜色
        disks = []
        colors = [RED, ORANGE, YELLOW, GREEN, BLUE, 
                 PURPLE, PINK, TEAL, MAROON, GOLD, LIGHT_BROWN]
        
        for i in range(DISKS):
            width = BASE_WIDTH * (0.4 + (DISKS - i) * 0.6 / DISKS)
            disk = Rectangle(
                width=width,
                height=DISK_HEIGHT,
                fill_color=colors[i],
                fill_opacity=1,
                stroke_width=1
            )
            disk.move_to(towers[0].get_bottom() + UP * (i * DISK_HEIGHT + DISK_HEIGHT/2))
            disks.append(disk)
        
        # 添加塔的标签
        labels = VGroup()
        for i, label in enumerate(['A', 'B', 'C']):
            text = Text(label, font_size=36).next_to(towers[i], DOWN)
            labels.add(text)
        
        # 显示初始状态
        self.play(
            Create(towers),
            Write(labels),
            *[Create(disk) for disk in disks]
        )
        self.wait(1)

        # 移动次数计数器
        move_count = Integer(0)
        move_count_text = Text("移动次数：").to_corner(UL)
        move_count.next_to(move_count_text, RIGHT)
        self.play(Write(move_count_text), Write(move_count))

        # 汉诺塔移动函数
        def move_disk(disk_index, from_tower, to_tower):
            disk = disks[disk_index]
            
            # 计算移动路径
            start_pos = disk.get_center()
            top_pos = towers[from_tower].get_top() + UP * DISKS * DISK_HEIGHT / 2
            target_top_pos = towers[to_tower].get_top() + UP * DISKS * DISK_HEIGHT / 2
            
            # 计算目标位置（要考虑目标柱子上已有的圆盘数量）
            disk_count = sum(1 for d in disks if abs(d.get_center()[0] - towers[to_tower].get_center()[0]) < 0.1)
            target_pos = towers[to_tower].get_bottom() + UP * (disk_count * DISK_HEIGHT + DISK_HEIGHT/2)
            
            # 执行移动动画
            self.play(
                disk.animate.move_to(top_pos),
                run_time=0.3
            )
            self.play(
                disk.animate.move_to(target_top_pos),
                run_time=0.3
            )
            self.play(
                disk.animate.move_to(target_pos),
                run_time=0.3
            )
            
            # 更新移动次数
            move_count.increment_value()

        # 汉诺塔递归函数
        def hanoi(n, from_tower, aux_tower, to_tower):
            if n > 0:
                # 将n-1个圆盘从起始柱移动到辅助柱
                hanoi(n-1, from_tower, to_tower, aux_tower)
                # 将最大的圆盘从起始柱移动到目标柱
                move_disk(n-1, from_tower, to_tower)
                # 将n-1个圆盘从辅助柱移动到目标柱
                hanoi(n-1, aux_tower, from_tower, to_tower)

        # 执行汉诺塔移动
        hanoi(DISKS, 0, 1, 2)

        # 显示完成信息
        completion_text = Text("完成!", color=GREEN).to_edge(DOWN)
        self.play(Write(completion_text))
        self.wait(2)

        # 显示总移动次数
        final_count = Text(
            f"总共移动了 {2**DISKS - 1} 次",
            font_size=36,
            color=YELLOW
        ).next_to(completion_text, UP)
        self.play(Write(final_count))
        self.wait(2)


