from manim import *
import random

config.frame_width = 16
config.frame_height = 9

class TimeManagement(Scene):
    def construct(self):
        # 配置
        BALL_RADIUS = 0.08
        PIPE_COLOR = WHITE
        PIPE_WIDTH = 0.2
        TOTAL_BALLS = 30
        VERTICAL_OFFSET = -0.5  # 添加垂直偏移量配置

        # 创建漏斗（上大下小）
        funnel = VGroup(
            CubicBezier(
                start_anchor=[-1.2, 4 + VERTICAL_OFFSET, 0],
                start_handle=[-1.2, 3.8 + VERTICAL_OFFSET, 0],
                end_handle=[-0.3, 3.5 + VERTICAL_OFFSET, 0],
                end_anchor=[-0.3, 3 + VERTICAL_OFFSET, 0]
            ),
            CubicBezier(
                start_anchor=[1.2, 4 + VERTICAL_OFFSET, 0],
                start_handle=[1.2, 3.8 + VERTICAL_OFFSET, 0],
                end_handle=[0.3, 3.5 + VERTICAL_OFFSET, 0],
                end_anchor=[0.3, 3 + VERTICAL_OFFSET, 0]
            ),
            Line([-0.3, 3 + VERTICAL_OFFSET, 0], [-0.2, 2 + VERTICAL_OFFSET, 0]),
            Line([0.3, 3 + VERTICAL_OFFSET, 0], [0.2, 2 + VERTICAL_OFFSET, 0])
        ).set_color(PIPE_COLOR)

        # 创建开关（简化为一根横线）
        switch = Line([-0.4, 2.2 + VERTICAL_OFFSET, 0], [0.4, 2.2 + VERTICAL_OFFSET, 0], color=RED)

        # 创建双线管道函数
        def create_double_line_path(start, end, control1, control2):
            path1 = CubicBezier(
                start_anchor=[start[0]-PIPE_WIDTH, start[1], 0],
                start_handle=[control1[0]-PIPE_WIDTH, control1[1], 0],
                end_handle=[control2[0]-PIPE_WIDTH, control2[1], 0],
                end_anchor=[end[0]-PIPE_WIDTH, end[1], 0]
            )
            path2 = CubicBezier(
                start_anchor=[start[0]+PIPE_WIDTH, start[1], 0],
                start_handle=[control1[0]+PIPE_WIDTH, control1[1], 0],
                end_handle=[control2[0]+PIPE_WIDTH, control2[1], 0],
                end_anchor=[end[0]+PIPE_WIDTH, end[1], 0]
            )
            return VGroup(path1, path2)

        # 创建各段管道
        pipe1 = create_double_line_path(
            [0, 2 + VERTICAL_OFFSET], [-1.2, 0.5 + VERTICAL_OFFSET],
            [0, 1.5 + VERTICAL_OFFSET], [-1, 1 + VERTICAL_OFFSET]
        )

        pipe2 = create_double_line_path(
            [-1.2, 0.5 + VERTICAL_OFFSET], [1.2, -0.5 + VERTICAL_OFFSET],
            [-1.4, 0 + VERTICAL_OFFSET], [1, 0 + VERTICAL_OFFSET]
        )

        pipe3 = create_double_line_path(
            [1.2, -0.5 + VERTICAL_OFFSET], [-1.2, -2 + VERTICAL_OFFSET],
            [1.4, -1 + VERTICAL_OFFSET], [-1, -1.5 + VERTICAL_OFFSET]
        )

        pipe4 = create_double_line_path(
            [-1.2, -2 + VERTICAL_OFFSET], [0, -2.5 + VERTICAL_OFFSET],
            [-1, -2.2 + VERTICAL_OFFSET], [0, -2.3 + VERTICAL_OFFSET]
        )

        main_pipe = VGroup(pipe1, pipe2, pipe3, pipe4).set_color(PIPE_COLOR)

        # 创建目标容器
        target_container = VGroup(
            Line([-0.6, -3 + VERTICAL_OFFSET, 0], [0.6, -3 + VERTICAL_OFFSET, 0]),
            Line([-0.6, -3 + VERTICAL_OFFSET, 0], [-0.5, -2.5 + VERTICAL_OFFSET, 0]),
            Line([0.6, -3 + VERTICAL_OFFSET, 0], [0.5, -2.5 + VERTICAL_OFFSET, 0])
        ).set_color(PIPE_COLOR)

        # 创建标签
        labels = VGroup(
            Text("你的时间", font="PingFang SC").scale(0.5).next_to(funnel, RIGHT),
            Text("社交", font="PingFang SC").scale(0.5).next_to([-1.2, 0.5 + VERTICAL_OFFSET, 0], LEFT),
            Text("玩手机", font="PingFang SC").scale(0.5).next_to([1.2, -0.5 + VERTICAL_OFFSET, 0], RIGHT),
            Text("拖延症", font="PingFang SC").scale(0.5).next_to([-1.2, -2 + VERTICAL_OFFSET, 0], LEFT),
            Text("你的目标", font="PingFang SC").scale(0.5).next_to(target_container, RIGHT)
        )

        # 创建中心路径
        center_paths = [
            CubicBezier(
                start_anchor=[0, 2 + VERTICAL_OFFSET, 0],
                start_handle=[0, 1.5 + VERTICAL_OFFSET, 0],
                end_handle=[-1, 1 + VERTICAL_OFFSET, 0],
                end_anchor=[-1.2, 0.5 + VERTICAL_OFFSET, 0]
            ),
            CubicBezier(
                start_anchor=[-1.2, 0.5 + VERTICAL_OFFSET, 0],
                start_handle=[-1.4, 0 + VERTICAL_OFFSET, 0],
                end_handle=[1, 0 + VERTICAL_OFFSET, 0],
                end_anchor=[1.2, -0.5 + VERTICAL_OFFSET, 0]
            ),
            CubicBezier(
                start_anchor=[1.2, -0.5 + VERTICAL_OFFSET, 0],
                start_handle=[1.4, -1 + VERTICAL_OFFSET, 0],
                end_handle=[-1, -1.5 + VERTICAL_OFFSET, 0],
                end_anchor=[-1.2, -2 + VERTICAL_OFFSET, 0]
            ),
            CubicBezier(
                start_anchor=[-1.2, -2 + VERTICAL_OFFSET, 0],
                start_handle=[-1, -2.2 + VERTICAL_OFFSET, 0],
                end_handle=[0, -2.3 + VERTICAL_OFFSET, 0],
                end_anchor=[0, -2.5 + VERTICAL_OFFSET, 0]
            )
        ]

        # 创建初始小球
        initial_balls = []
        ball_positions = []

        # 计算漏斗中的球的位置
        rows = 6
        for row in range(rows):
            balls_in_row = row + 1
            y_pos = 4.2 + VERTICAL_OFFSET - row * BALL_RADIUS * 2
            for i in range(balls_in_row):
                x_start = -(balls_in_row - 1) * BALL_RADIUS
                x_pos = x_start + i * BALL_RADIUS * 2
                ball_positions.append([x_pos, y_pos, 0])

        # 创建初始小球
        for pos in ball_positions[:TOTAL_BALLS]:
            ball = Circle(radius=BALL_RADIUS, fill_opacity=1, color=YELLOW)
            ball.move_to(pos)
            initial_balls.append(ball)

        # 目标位置
        target_positions = [
            [-0.3, -2.9 + VERTICAL_OFFSET, 0],
            [0.3, -2.9 + VERTICAL_OFFSET, 0]
        ]

        # 显示基本结构和初始小球
        self.play(
            Create(funnel),
            Create(main_pipe),
            Create(target_container),
            Create(switch),
            Write(labels)
        )

        self.play(*[FadeIn(ball) for ball in initial_balls])
        self.wait(1)

        # 开关打开动画（简化为颜色变化）
        self.play(
            switch.animate.set_color(GREEN)
        )
        self.wait(0.5)

        # 小球流动动画
        balls_in_target = 0
        for i, ball in enumerate(initial_balls):
            rand = random.random()

            if (rand < 0.2 and balls_in_target < 2) or (i >= TOTAL_BALLS - (2 - balls_in_target)):
                for path in center_paths:
                    self.play(MoveAlongPath(ball, path), run_time=0.25)

                self.play(
                    ball.animate.move_to(target_positions[balls_in_target]),
                    run_time=0.2
                )
                balls_in_target += 1
            else:
                if rand < 0.35:
                    self.play(MoveAlongPath(ball, center_paths[0]), run_time=0.8)
                    self.play(FadeOut(ball))
                elif rand < 0.70:
                    self.play(
                        MoveAlongPath(ball, center_paths[0]),
                        run_time=0.4
                    )
                    self.play(
                        MoveAlongPath(ball, center_paths[1]),
                        run_time=0.4
                    )
                    self.play(FadeOut(ball))
                else:
                    self.play(
                        MoveAlongPath(ball, center_paths[0]),
                        run_time=0.3
                    )
                    self.play(
                        MoveAlongPath(ball, center_paths[1]),
                        run_time=0.3
                    )
                    self.play(
                        MoveAlongPath(ball, center_paths[2]),
                        run_time=0.3
                    )
                    self.play(FadeOut(ball))

        self.wait(2)

