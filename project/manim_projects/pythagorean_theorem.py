from manim import *
import numpy as np

config.frame_width = 16
config.frame_height = 9

# 配置 LaTeX 模板
tex_template = TexTemplate()
tex_template.add_to_preamble(r"\usepackage{amsmath}")

# 颜色常量定义
MAIN_COLOR = "#FF4444"
SECONDARY_COLOR = "#4444FF"
RESULT_COLOR = "#44AA44"
EMPHASIS_COLOR = "#FFFF00"

class PythagoreanTheorem(Scene):
    def __init__(self):
        super().__init__()
        self.tex_template = tex_template

    def construct(self):
        # === 第一部分：概念导入 ===
        def create_introduction(self):
            # 标题
            title = Text(
                "勾股定理", 
                font="PingFang SC", 
                font_size=36
            ).to_edge(UP)
            
            # 历史背景
            history_text = Text(
                "古代测量问题",
                font="PingFang SC",
                font_size=28,
                color=SECONDARY_COLOR
            ).next_to(title, DOWN, buff=0.5)

            # 创建生活场景示例
            building = VGroup(
                # 房子的底部
                Rectangle(width=2, height=1.5, color=WHITE),
                # 房顶（三角形）
                Polygon(
                    [-1, 1.5, 0],
                    [1, 1.5, 0],
                    [0, 2.5, 0],
                    color=WHITE
                )
            )
            
            # 创建梯子和测量线
            ladder = Line(
                start=[-0.5, 0, 0],
                end=[0.5, 2, 0],
                color=MAIN_COLOR
            )
            
            # 测量标注
            height_line = DashedLine(
                start=[0.5, 0, 0],
                end=[0.5, 2, 0],
                color=SECONDARY_COLOR
            )
            width_line = DashedLine(
                start=[-0.5, 0, 0],
                end=[0.5, 0, 0],
                color=SECONDARY_COLOR
            )

            # 问题文本
            question = Text(
                "如何计算梯子的长度？",
                font="PingFang SC",
                font_size=24,
                color=EMPHASIS_COLOR
            ).next_to(building, DOWN, buff=1.2)

            # 将所有元素组合并居中
            scene_group = VGroup(building, ladder, height_line, width_line)
            scene_group.move_to(ORIGIN)
            
            # 动画序列
            self.play(Write(title))
            self.play(Write(history_text))
            self.wait(1)
            
            self.play(Create(building), run_time=2)
            self.play(
                Create(ladder),
                Create(height_line),
                Create(width_line),
                run_time=2
            )
            self.play(Write(question))
            self.wait(2)

            return VGroup(title, history_text, scene_group, question)

        intro_scene = create_introduction(self)

        # === 第二部分：定理发现 ===
        def create_theorem_discovery(self):
            # 清除前一个场景
            self.clear()  # 确保完全清除

            # 创建标题
            subtitle = Text(
                "发现规律",
                font="PingFang SC",
                font_size=32,
                color=SECONDARY_COLOR
            ).to_edge(UP)

            # 创建网格背景
            grid = NumberPlane(
                x_range=[-5, 5],
                y_range=[-3, 3],
                background_line_style={
                    "stroke_opacity": 0.2
                }
            ).scale(0.8)  # 缩小网格

            # 创建直角三角形
            triangle = Polygon(
                [-1, -1, 0],
                [1, -1, 0],
                [-1, 1, 0],
                color=MAIN_COLOR
            ).scale(1.2)  # 放大三角形

            # 直角符号
            right_angle = Square(
                side_length=0.2,
                color=SECONDARY_COLOR
            ).move_to(triangle.get_vertices()[0]).shift(RIGHT * 0.1 + UP * 0.1)

            # 添加边长标注（修改后的MathTex使用）
            a_label = Tex("$a$", color=MAIN_COLOR).next_to(
                Line(triangle.get_vertices()[0], triangle.get_vertices()[1]).get_center(),
                DOWN, buff=0.2
            )
            b_label = Tex("$b$", color=MAIN_COLOR).next_to(
                Line(triangle.get_vertices()[0], triangle.get_vertices()[2]).get_center(),
                LEFT, buff=0.2
            )
            c_label = Tex("$c$", color=MAIN_COLOR).next_to(
                Line(triangle.get_vertices()[1], triangle.get_vertices()[2]).get_center(),
                UP + RIGHT, buff=0.2
            )

            # 组合三角形相关元素
            triangle_group = VGroup(triangle, right_angle, a_label, b_label, c_label)
            triangle_group.move_to(ORIGIN)

            # 动画序列
            self.play(Write(subtitle))
            self.play(Create(grid, run_time=1))
            self.play(Create(triangle), run_time=1)
            self.play(Create(right_angle))
            self.play(
                Write(a_label),
                Write(b_label),
                Write(c_label)
            )

            # 添加公式（修改后的写法）
            formula = Tex(
                "$a^2 + b^2 = c^2$",
                color=RESULT_COLOR
            ).scale(1.5).next_to(triangle_group, DOWN, buff=1)

            self.play(Write(formula))
            self.wait(2)

            return VGroup(subtitle, grid, triangle_group, formula)

        discovery_scene = create_theorem_discovery(self)

        def create_theorem_proof(self):
            # 清除前一个场景
            self.clear()

            # 创建标题
            proof_title = Text(
                "勾股定理证明",
                font="PingFang SC",
                font_size=32,
                color=SECONDARY_COLOR
            ).to_edge(UP)

            # 设置基础单位长度（用于保持比例）
            unit = 0.8  # 可以调整这个值来改变整体大小

            # 定义三角形的三个顶点（使用3-4-5的比例）
            start_point = [-4, -2, 0]  # 从-5改为-4，向右移动
            bottom_point = [-4 + 3 * unit, -2, 0]  # 相应调整
            top_point = [-4, -2 + 4 * unit, 0]  # 相应调整

            # 分别创建三边
            side_a = Line(start_point, bottom_point, color=MAIN_COLOR)  # 底边，长3
            side_b = Line(start_point, top_point, color=SECONDARY_COLOR)  # 高，长4
            side_c = Line(bottom_point, top_point, color=RESULT_COLOR)  # 斜边，长5

            # 创建直角符号
            right_angle = Square(
                side_length=0.2,
                color=WHITE
            ).move_to(start_point).shift(RIGHT * 0.1 + UP * 0.1)

            # 标注三边
            a_label = Tex("$a=3$", color=MAIN_COLOR).next_to(
                side_a.get_center(), DOWN, buff=0.2
            )
            b_label = Tex("$b=4$", color=SECONDARY_COLOR).next_to(
                side_b.get_center(), LEFT, buff=0.2
            ).shift(DOWN * 0.5)  # 向下移动

            c_label = Tex("$c=5$", color=RESULT_COLOR).next_to(
                side_c.get_center(),
                UP + RIGHT,
                buff=0.3  # 增加buff值
            ).shift(RIGHT * 0.2)  # 向右微调

            # 组合三角形
            triangle_group = VGroup(side_a, side_b, side_c, right_angle)
            triangle_group.shift(RIGHT * 0.5)  # 整体再向右移动一点

            # 正方形的位置会自动跟随三角形移动，因为是相对位置
            square_a = Square(
                side_length=3 * unit,
                stroke_color=MAIN_COLOR,
                fill_color=MAIN_COLOR,
                fill_opacity=0.2
            ).next_to(side_a, RIGHT, buff=0.1)

            square_b = Square(
                side_length=4 * unit,
                stroke_color=SECONDARY_COLOR,
                fill_color=SECONDARY_COLOR,
                fill_opacity=0.2
            ).next_to(side_b, LEFT, buff=0.1)

            # c的正方形位置微调
            square_c = Square(
                side_length=5 * unit,
                stroke_color=RESULT_COLOR,
                fill_color=RESULT_COLOR,
                fill_opacity=0.2
            ).next_to(triangle_group, RIGHT, buff=1)
            square_c.shift(LEFT * 2 + UP * 1.7)

            # 面积标注
            area_a = VGroup(
                Tex("$a^2$", color=MAIN_COLOR),
                Text("=9", font="PingFang SC", font_size=24, color=MAIN_COLOR)
            ).arrange(RIGHT, buff=0.1).move_to(square_a)

            area_b = VGroup(
                Tex("$b^2$", color=SECONDARY_COLOR),
                Text("=16", font="PingFang SC", font_size=24, color=SECONDARY_COLOR)
            ).arrange(RIGHT, buff=0.1).move_to(square_b)

            area_c = VGroup(
                Tex("$c^2$", color=RESULT_COLOR),
                Text("=25", font="PingFang SC", font_size=24, color=RESULT_COLOR)
            ).arrange(RIGHT, buff=0.1).move_to(square_c)

            # 创建证明步骤说明（移到更右边）
            proof_steps = VGroup(
                Text("证明步骤：", font="PingFang SC", font_size=28, color=SECONDARY_COLOR),
                Text("1. 作直角三角形两直角边上的正方形", font="PingFang SC", font_size=24),
                Text("2. 计算两个正方形的面积", font="PingFang SC", font_size=24),
                Text("3. 计算斜边上正方形的面积", font="PingFang SC", font_size=24)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.3).to_edge(RIGHT, buff=0.4)

            # 计算过程
            calc_process = VGroup(
                Tex("$a^2 = 3^2 = 9$", color=MAIN_COLOR),
                Tex("$b^2 = 4^2 = 16$", color=SECONDARY_COLOR),
                Tex("$a^2 + b^2 = 9 + 16 = 25$"),
                Tex("$c^2 = 5^2 = 25$", color=RESULT_COLOR)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).next_to(proof_steps, DOWN, buff=1)

            # 最终结论
            conclusion = Tex(
                "$\\therefore a^2 + b^2 = c^2$",
                color=RESULT_COLOR
            ).scale(1.2).next_to(calc_process, DOWN, buff=0.8)

            # 动画序列
            self.play(Write(proof_title))

            # 显示三角形边和标注
            self.play(
                Create(side_a),
                Create(side_b),
                Create(side_c),
            )
            self.play(Create(right_angle))
            self.play(
                Write(a_label),
                Write(b_label),
                Write(c_label)
            )
            self.wait()

            # 显示第一个步骤和正方形
            self.play(Write(proof_steps[0:2]))
            self.play(
                Create(square_a),
                Create(square_b),
                run_time=2
            )
            self.wait()

            # 显示第二个步骤和面积计算
            self.play(Write(proof_steps[2]))
            self.play(
                Write(area_a),
                Write(area_b)
            )
            self.play(Write(calc_process[:2]))
            self.wait()

            # 显示第三个步骤和最终结论
            self.play(Write(proof_steps[3]))
            self.play(Create(square_c))
            self.play(Write(area_c))
            self.play(Write(calc_process[2:]))
            self.play(Write(conclusion))
            self.wait(2)

            return VGroup(
                proof_title, triangle_group,
                square_a, square_b, square_c,
                area_a, area_b, area_c,
                proof_steps, calc_process, conclusion
            )

        proof_scene = create_theorem_proof(self)

        # === 第四部分：应用演练 ===
        def create_applications(self):
            # 清除前一个场景
            self.clear()
        
            # 创建标题
            app_title = Text(
                "实际应用",
                font="PingFang SC",
                font_size=32,
                color=SECONDARY_COLOR
            ).to_edge(UP)
        
            # 创建例题1：基础计算
            example1 = VGroup(
                Text("例1：已知直角三角形两直角边分别为3和4，求斜边。",
                     font="PingFang SC", font_size=24)
            ).next_to(app_title, DOWN, buff=0.8)
        
            # 创建例题1的图示
            triangle1 = Polygon(
                [0, 0, 0],
                [3, 0, 0],
                [0, 4, 0],
                color=MAIN_COLOR
            ).scale(0.3).next_to(example1, DOWN, buff=0.5)
        
            # 添加标注
            labels1 = VGroup(
                # 底边标注
                Text("3", font="PingFang SC", font_size=20).next_to(
                    Line(triangle1.get_vertices()[0], triangle1.get_vertices()[1]).get_center(),
                    DOWN, buff=0.1
                ),
                # 高度标注
                Text("4", font="PingFang SC", font_size=20).next_to(
                    Line(triangle1.get_vertices()[0], triangle1.get_vertices()[2]).get_center(),
                    LEFT, buff=0.1
                ),
                # 斜边标注 - 使用斜边的中点
                Text("?", font="PingFang SC", font_size=20).next_to(
                    Line(triangle1.get_vertices()[1], triangle1.get_vertices()[2]).get_center(),
                    UP + RIGHT, buff=0.1
                )
            )
 
            # 例题1的解答过程
            solution1 = VGroup(
                Tex("$c^2 = 3^2 + 4^2$"),
                Tex("$= 9 + 16$"),
                Tex("$= 25$"),
                Tex("$c = 5$")
            ).arrange(DOWN, aligned_edge=LEFT).next_to(triangle1, RIGHT, buff=2).shift(DOWN * 0.5)  # 向下移动
        
            # 创建例题2
            example2 = VGroup(
                Text("例2：一架梯子斜靠在墙上，地面距离为6米，高度为8米，求梯子长度。",
                     font="PingFang SC", font_size=24)
            ).next_to(example1, DOWN, buff=3)
        
            # 创建梯子问题的图示（先创建各个部分）
            wall = Line([0, 0, 0], [0, 3, 0], color=WHITE)
            ground = Line([0, 0, 0], [-3, 0, 0], color=WHITE)
            ladder = Line([-3, 0, 0], [0, 3, 0], color=MAIN_COLOR)

            # 组合梯子图示并调整位置
            ladder_diagram = VGroup(wall, ground, ladder)
            ladder_diagram.scale(0.8).next_to(example2, DOWN, buff=0.8).align_to(triangle1, LEFT).shift(
                LEFT * 2)  # 向左移动

            # 添加测量标注（标注会跟随ladder_diagram移动）
            measurements = VGroup(
                Text("6m", font="PingFang SC", font_size=20).next_to(ground, DOWN, buff=0.1),
                Text("8m", font="PingFang SC", font_size=20).next_to(wall, RIGHT, buff=0.1),
                Text("?", font="PingFang SC", font_size=20).next_to(ladder.get_center(), UP + LEFT, buff=0.2)
            )

            # 例题2的解答过程
            solution2 = VGroup(
                Tex("$c^2 = 6^2 + 8^2$"),
                Tex("$= 36 + 64$"),
                Tex("$= 100$"),
                VGroup(
                    Tex("$c = 10$"),
                    Text("米", font="PingFang SC", font_size=24)
                ).arrange(RIGHT, buff=0.1)
            ).arrange(DOWN, aligned_edge=LEFT).next_to(ladder_diagram, RIGHT, buff=2).align_to(solution1, LEFT)
        
            # 动画序列
            self.play(Write(app_title))
            
            # 例题1动画
            self.play(Write(example1))
            self.play(Create(triangle1), Write(labels1))
            self.play(Write(solution1), run_time=2)
            self.wait()
            
            # 例题2动画
            self.play(Write(example2))
            self.play(Create(ladder_diagram), Write(measurements))
            self.play(Write(solution2), run_time=2)
            self.wait(2)
        
            return VGroup(
                app_title, example1, triangle1, labels1, solution1,
                example2, ladder_diagram, measurements, solution2
            )

        applications_scene = create_applications(self)

        # === 总结部分 ===
        def create_summary(self):
            # 清除前一个场景
            self.clear()

            # 创建总结标题
            summary_title = Text(
                "知识总结",
                font="PingFang SC",
                font_size=32,
                color=EMPHASIS_COLOR
            ).to_edge(UP)

            # 创建中间的三角形示意图
            demo_triangle = VGroup(
                Polygon(
                    [-1, -1, 0],
                    [1, -1, 0],
                    [-1, 1, 0],
                    color=MAIN_COLOR
                ),
                Square(
                    side_length=0.2,
                    color=SECONDARY_COLOR
                ).move_to([-1, -1, 0]).shift(RIGHT * 0.1 + UP * 0.1)
            ).scale(0.8)

            # 在三角形周围添加公式（修改后的写法）
            formula = Tex("$a^2 + b^2 = c^2$", color=RESULT_COLOR)
            demo_group = VGroup(demo_triangle, formula)
            demo_group.arrange(DOWN, buff=0.5)
            demo_group.move_to([-4, 0, 0])

            # 添加变量标注
            labels = VGroup(
                Tex("$a$", color=MAIN_COLOR).next_to(demo_triangle, DOWN, buff=0.2),
                Tex("$b$", color=MAIN_COLOR).next_to(demo_triangle, LEFT, buff=0.2),
                Tex("$c$", color=MAIN_COLOR).next_to(
                    demo_triangle, UP + RIGHT, buff=0.1  # 减小 buff 值
                ).shift(LEFT * 0.5 + DOWN * 0.5)  # 稍微向左移动一点，更靠近斜边
            )

            demo_group.add(labels)

            # 创建要点总结
            summary_points = VGroup(
                Text("1. 勾股定理仅适用于直角三角形", font="PingFang SC", font_size=24),
                Text("2. 两直角边的平方和等于斜边的平方", font="PingFang SC", font_size=24),
                Text("3. 可用于计算边长和判断直角", font="PingFang SC", font_size=24),
                Text("4. 广泛应用于实际测量问题", font="PingFang SC", font_size=24)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
            summary_points.next_to(summary_title, DOWN, buff=0.8).shift(RIGHT * 2)

            # 创建应用提示
            tips = VGroup(
                Text("注意事项：", font="PingFang SC", font_size=28, color=MAIN_COLOR),
                Text("• 注意区分直角边和斜边", font="PingFang SC", font_size=24),
                Text("• 计算时需要考虑单位统一", font="PingFang SC", font_size=24),
                Text("• 结果要验证合理性", font="PingFang SC", font_size=24)
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
            tips.next_to(summary_points, DOWN, buff=0.8)

            # 动画序列
            self.play(Write(summary_title))
            self.play(Create(demo_group))
            self.play(Write(summary_points), run_time=2)
            self.play(Write(tips), run_time=2)
            self.wait(2)

            # 结束语
            final_text = Text(
                "谢谢观看！",
                font="PingFang SC",
                font_size=36,
                color=BLUE
            ).move_to(ORIGIN)
            
            self.play(
                FadeOut(summary_title),
                FadeOut(demo_group),
                FadeOut(summary_points),
                FadeOut(tips)
            )
            self.play(Write(final_text))
            self.wait(2)

        create_summary(self)


