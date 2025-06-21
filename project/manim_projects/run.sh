brew install python@3.11
brew install pkg-config cairo

/usr/local/bin/python3.11 -m venv manim_env
source manim_env/bin/activate

pip install manim -i https://pypi.tuna.tsinghua.edu.cn/simple

manim -pql hanoi_tower.py HanoiTower
manim -pql pythagorean_theorem.py PythagoreanTheorem
manim -pql time_management.py TimeManagement
