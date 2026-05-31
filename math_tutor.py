import streamlit as st
import plotly.graph_objects as go
import numpy as np
import random
import re

# ============================================================
# 0. 页面配置
# ============================================================
st.set_page_config(page_title="MathTutor高等数学学习平台", layout="wide", page_icon="📐")

# ============================================================
# 1. 初始化 Session State
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "home"        # home / detail / planning
if "selected_topic" not in st.session_state:
    st.session_state.selected_topic = None
if "ratings" not in st.session_state:
    st.session_state.ratings = {}          # {topic_id: star_count}
if "history" not in st.session_state:
    st.session_state.history = {}          # {topic_id: {"visited":bool, "questions_correct":int, "questions_wrong":int, "qas":[]}}
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

# ============================================================
# 2. 知识图谱数据（覆盖高数上下册核心知识点）
# ============================================================

# 颜色方案 - 12个知识群组
GROUP_COLORS = {
    "函数与预备知识": "#FF6B6B",     # 红
    "极限与连续":     "#FF9F43",     # 橙
    "导数与微分":     "#FECA57",     # 黄
    "中值定理与应用": "#48DBFB",     # 亮蓝
    "积分学":         "#1DD1A1",     # 绿
    "定积分应用":     "#5F27CD",     # 紫
    "空间解析几何":   "#54A0FF",     # 蓝
    "多元函数微分":   "#FF6FA4",     # 粉
    "重积分":         "#00D2D3",     # 青
    "曲线曲面积分":   "#F368E0",     # 品红
    "无穷级数":       "#E17055",     # 棕橙
    "微分方程":       "#2ED573",     # 草绿
}

# 所有知识点节点
TOPICS = [
    # ---- 函数与预备知识 ----
    {"id":"set",          "name":"集合与实数集",       "group":"函数与预备知识", "desc":"集合是数学的基础语言，实数集R是高等数学的核心研究对象。包含区间、邻域等概念。", "methods":"1. 区间表示法：(a,b)、[a,b]等\n2. 邻域：U(a,δ) = {x | |x-a| < δ}\n3. 集合运算：交、并、补、差"},
    {"id":"function",     "name":"函数概念与性质",     "group":"函数与预备知识", "desc":"函数是从定义域到值域的映射，是高等数学的基本研究对象。包括有界性、单调性、奇偶性、周期性。", "methods":"1. 判断有界性：|f(x)| ≤ M\n2. 单调性：用导数符号f'(x) > 0 / < 0\n3. 奇偶性：f(-x) = f(x)偶 / f(-x) = -f(x)奇"},
    {"id":"compfunc",     "name":"反函数与复合函数",   "group":"函数与预备知识", "desc":"复合函数f(g(x))是函数嵌套，反函数是逆映射。复合函数求导的链式法则是微分学的核心。", "methods":"1. 复合函数：从内到外逐层分析\n2. 反函数：y=f(x) => x=f⁻¹(y)\n3. 复合函数定义域：内层值域⊆外层定义域"},
    
    # ---- 极限与连续 ----
    {"id":"seq_limit",    "name":"数列极限",           "group":"极限与连续",     "desc":"数列极限是当n→∞时数列趋近的确定值。ε-N语言是严格的极限定义。", "methods":"1. ε-N定义：∀ε>0, ∃N, n>N ⇒ |aₙ-A|<ε\n2. 极限四则运算\n3. 夹逼准则：bₙ≤aₙ≤cₙ, bₙ,cₙ→A ⇒ aₙ→A"},
    {"id":"func_limit",   "name":"函数极限",           "group":"极限与连续",     "desc":"函数极限描述x→x₀时f(x)的趋近值。左右极限概念是判断极限存在的重要工具。", "methods":"1. 左极限=右极限 ⇔ 极限存在\n2. 两个重要极限：lim sinx/x=1, lim(1+1/x)ˣ=e\n3. 无穷小替换：x→0时sinx~x, tanx~x"},
    {"id":"infinity",     "name":"无穷小与无穷大",     "group":"极限与连续",     "desc":"无穷小是以0为极限的变量，无穷大是绝对值无限增大的变量。无穷小的比较是极限计算的关键。", "methods":"1. 高阶/同阶/等价无穷小\n2. 等价无穷小替换（乘除因子可换）\n3. 注意：加减法不能随意替换"},
    {"id":"continuity",   "name":"连续函数",           "group":"极限与连续",     "desc":"连续是函数在一点处极限值等于函数值。间断点分为可去、跳跃、无穷、振荡四类。", "methods":"1. 连续定义：lim f(x)=f(x₀)\n2. 间断点分类：左右极限存在→第一类；否则第二类\n3. 闭区间上连续：有界、最值、介值定理"},
    
    # ---- 导数与微分 ----
    {"id":"derivative",   "name":"导数概念",           "group":"导数与微分",     "desc":"导数是函数在某点的变化率，几何意义为切线斜率。f'(x₀)=lim(f(x)-f(x₀))/(x-x₀)", "methods":"1. 导数定义求导（四步法）\n2. 可导⇔左导数=右导数\n3. 可导必连续，连续不一定可导"},
    {"id":"diff_rules",   "name":"求导法则",           "group":"导数与微分",     "desc":"包括四则运算法则、复合函数链式法则、反函数求导法则。是导数计算的工具集。", "methods":"1. (u±v)'=u'±v', (uv)'=u'v+uv', (u/v)'=(u'v-uv')/v²\n2. 链式法则：f(g(x))'=f'(g(x))·g'(x)\n3. 牢记基本初等函数导数公式"},
    {"id":"higher_der",   "name":"高阶导数",           "group":"导数与微分",     "desc":"n阶导数是导数的导数。莱布尼茨公式用于求乘积的高阶导数。", "methods":"1. 直接逐阶求导\n2. 莱布尼茨公式：(uv)^(n)=∑C(n,k)u^(n-k)v^(k)\n3. 常用高阶导数：sinx, cosx, eˣ的n阶导有规律"},
    {"id":"implicit_der", "name":"隐函数与参数方程求导","group":"导数与微分",     "desc":"隐函数求导是将y视为x的函数，方程两边同时对x求导。参数方程求导用dy/dx=(dy/dt)/(dx/dt)", "methods":"1. 隐函数：两边对x求导，解出y'\n2. 参数方程：dy/dx=(dy/dt)/(dx/dt)\n3. 相关变化率：建立关系→两边求导"},
    {"id":"differential", "name":"微分",               "group":"导数与微分",     "desc":"微分dy=f'(x)dx是函数增量的线性主部。用于近似计算和误差估计。", "methods":"1. dy=f'(x)dx\n2. 近似公式：f(x+Δx)≈f(x)+f'(x)Δx\n3. 一阶微分形式不变性"},
    
    # ---- 中值定理与应用 ----
    {"id":"mean_theorem", "name":"微分中值定理",       "group":"中值定理与应用", "desc":"包括Rolle、Lagrange、Cauchy三大中值定理，建立了函数与导数的桥梁。", "methods":"1. Rolle：f(a)=f(b)⇒存在ξ使f'(ξ)=0\n2. Lagrange：f(b)-f(a)=f'(ξ)(b-a)\n3. Cauchy：用于证明洛必达法则"},
    {"id":"lhopital",     "name":"洛必达法则",         "group":"中值定理与应用", "desc":"用于求解0/0和∞/∞型不定式极限。分子分母分别求导后再求极限。", "methods":"1. 0/0或∞/∞型才能用\n2. 分子分母分别求导\n3. 可多次使用，直到求出极限"},
    {"id":"taylor",       "name":"泰勒公式",           "group":"中值定理与应用", "desc":"用多项式逼近函数。泰勒公式是微分学的巅峰成果。", "methods":"1. f(x)=∑f⁽ᵏ⁾(x₀)/k!·(x-x₀)ᵏ + Rₙ(x)\n2. 麦克劳林公式：x₀=0的特例\n3. 常用展开：eˣ, sinx, cosx, ln(1+x)"},
    {"id":"extremum",     "name":"函数的极值与最值",   "group":"中值定理与应用", "desc":"利用导数判断函数单调性和极值。一阶导=0的点是驻点，还需二阶导判断。", "methods":"1. f'(x)=0⇒驻点（可能极值点）\n2. f''(x₀)>0极小，f''(x₀)<0极大\n3. 闭区间最值：端点+极值点比较"},
    {"id":"curve_sketch", "name":"函数图形讨论",       "group":"中值定理与应用", "desc":"利用导数分析函数图形：单调区间、凹凸性、渐近线、拐点。", "methods":"1. 一阶导定单调，二阶导定凹凸\n2. 渐近线：水平(y=c)、垂直(x=a)、斜(y=kx+b)\n3. 拐点：f''(x)变号处"},
    
    # ---- 积分学 ----
    {"id":"def_integral", "name":"定积分概念",         "group":"积分学",         "desc":"定积分是分割、近似、求和、取极限的过程。黎曼和的极限就是定积分。", "methods":"1. 定积分定义：∫f(x)dx=lim∑f(ξᵢ)Δxᵢ\n2. 几何意义：曲线下面积\n3. 可积条件：连续或只有有限个第一类间断点"},
    {"id":"indef_integral","name":"不定积分",          "group":"积分学",         "desc":"不定积分是求导的逆运算，F'(x)=f(x)，记作∫f(x)dx=F(x)+C", "methods":"1. 直接积分法：利用基本积分公式\n2. 注意：要加常数C\n3. 不定积分结果可互化（差一个常数）"},
    {"id":"substitution", "name":"换元积分法",         "group":"积分学",         "desc":"第一类换元（凑微分）和第二类换元（变量替换），是积分最重要的技巧。", "methods":"1. 第一类：∫f(φ(x))φ'(x)dx = ∫f(u)du\n2. 第二类：x=g(t)，dx=g'(t)dt\n3. 常用代换：三角代换、根式代换"},
    {"id":"by_parts",     "name":"分部积分法",         "group":"积分学",         "desc":"∫u dv = uv - ∫v du，乘积的积分公式，关键是选对u和v。", "methods":"1. 选择u的原则：反对幂指三（顺序前为u）\n2. 反函数/对数→u；幂函数→u或v\n3. 可多次分部，也可解方程求积分"},
    {"id":"newton_leibniz","name":"牛顿-莱布尼茨公式", "group":"积分学",         "desc":"定积分=原函数在上下限处的差值，∫ᵇₐ f(x)dx=F(b)-F(a)", "methods":"1. 先找原函数，再代入上下限\n2. 定积分换元要换限\n3. 注意被积函数的奇偶性简化计算"},
    {"id":"improper_int", "name":"广义积分",           "group":"积分学",         "desc":"积分区间无限或被积函数无界的积分。通过极限来定义。", "methods":"1. 无穷限：∫[a,∞)f(x)dx = lim∫[a,R]f(x)dx\n2. 无界函数：瑕积分\n3. 收敛性判断：比较判别法"},
    
    # ---- 定积分应用 ----
    {"id":"integral_app_area", "name":"平面图形面积",  "group":"定积分应用",     "desc":"用定积分计算曲线围成的面积。直角坐标∫|f(x)-g(x)|dx，极坐标∫½r²dθ", "methods":"1. 直角坐标：A=∫|y₁-y₂|dx\n2. 极坐标：A=½∫r²dθ\n3. 注意：上下边界函数要分清"},
    {"id":"integral_app_volume","name":"旋转体体积",   "group":"定积分应用",     "desc":"曲线绕坐标轴旋转形成的立体体积。圆盘法和壳层法。", "methods":"1. 绕x轴：V=π∫[f(x)]²dx\n2. 绕y轴：V=2π∫x·f(x)dx\n3. 已知截面面积：V=∫A(x)dx"},
    {"id":"integral_app_arc",  "name":"弧长与旋转曲面","group":"定积分应用",     "desc":"曲线弧长和旋转曲面面积的积分公式。需计算切线长和弧微分。", "methods":"1. 弧长：ds=√(1+(y')²)dx\n2. 旋转曲面：S=2π∫y·ds\n3. 参数方程弧长：s=∫√((x')²+(y')²)dt"},
    
    # ---- 空间解析几何 ----
    {"id":"vector",       "name":"向量运算",           "group":"空间解析几何",   "desc":"向量的线性运算、数量积（点乘）和向量积（叉乘）。是解析几何的基础。", "methods":"1. 数量积：a·b=|a||b|cosθ，结果标量\n2. 向量积：a×b，结果向量，垂直a,b\n3. 混合积：(a×b)·c = 体积"},
    {"id":"plane_line",   "name":"平面与直线方程",     "group":"空间解析几何",   "desc":"平面的点法式方程、直线的对称式方程。空间几何问题的解析表达。", "methods":"1. 平面：A(x-x₀)+B(y-y₀)+C(z-z₀)=0\n2. 直线：(x-x₀)/m = (y-y₀)/n = (z-z₀)/p\n3. 距离公式：点到平面距离"},
    {"id":"surface_curve","name":"曲面与空间曲线",     "group":"空间解析几何",   "desc":"球面、柱面、旋转面等常见曲面。空间曲线是曲面的交线。", "methods":"1. 球面：x²+y²+z²=R²\n2. 柱面：缺少一个变量的方程\n3. 旋转面：母曲线绕轴旋转"},
    
    # ---- 多元函数微分 ----
    {"id":"multi_func",   "name":"多元函数概念",       "group":"多元函数微分",   "desc":"多元函数z=f(x,y)是R²→R的映射。等值线是理解多元函数的可视化工具。", "methods":"1. 定义域为平面区域\n2. 图形为曲面\n3. 等值线：f(x,y)=C的平面截线"},
    {"id":"partial_der",  "name":"偏导数",             "group":"多元函数微分",   "desc":"对多元函数中一个变量求导，其余变量视为常数。f_x=∂f/∂x", "methods":"1. 对x求偏导：y看作常数\n2. 高阶偏导：f_xy = ∂²f/∂x∂y\n3. 混合偏导相等定理（连续时）"},
    {"id":"total_diff",   "name":"全微分",             "group":"多元函数微分",   "desc":"dz = f_x·dx + f_y·dy，是多元函数增量线性主部。可微是比偏导存在更强的条件。", "methods":"1. 全微分公式：dz=∂z/∂x·dx + ∂z/∂y·dy\n2. 可微条件：偏导连续⇒可微\n3. 近似计算：Δz ≈ dz"},
    {"id":"chain_rule_multi","name":"多元复合函数求导", "group":"多元函数微分",   "desc":"链法则：z=f(u,v), u=u(x,y)⇒∂z/∂x = ∂z/∂u·∂u/∂x + ∂z/∂v·∂v/∂x", "methods":"1. 画出依赖关系树\n2. 每条路径偏导相乘\n3. 全导数：一元函数情况"},
    {"id":"gradient",     "name":"方向导数与梯度",     "group":"多元函数微分",   "desc":"梯度∇f=(f_x,f_y)指向函数增加最快的方向。方向导数是梯度在特定方向上的投影。", "methods":"1. 梯度：∇f=(∂f/∂x, ∂f/∂y)\n2. 方向导数：D_u f = ∇f·u\n3. 梯度方向增长最快，反方向下降最快"},
    {"id":"multi_extremum","name":"多元函数极值",       "group":"多元函数微分",   "desc":"利用偏导寻找多元函数极值。拉格朗日乘数法用于条件极值。", "methods":"1. 驻点：f_x=0, f_y=0\n2. 判别法：AC-B²>0极值，<0鞍点\n3. 条件极值：构造拉格朗日函数L=f+λg"},
    
    # ---- 重积分 ----
    {"id":"double_int",   "name":"二重积分",           "group":"重积分",         "desc":"二重积分是二元函数在平面区域上的积分。直角坐标和极坐标是两种主要计算方法。", "methods":"1. 直角坐标：X型/Y型区域\n2. 极坐标：∫∫f(rcosθ,rsinθ)rdrdθ\n3. 换序积分：改变积分次序"},
    {"id":"triple_int",   "name":"三重积分",           "group":"重积分",         "desc":"三重积分是三元函数在空间区域上的积分。可用直角坐标、柱坐标、球坐标。", "methods":"1. 直角坐标：先一后二/先二后一\n2. 柱坐标：x=rcosθ, y=rsinθ, z=z\n3. 球坐标：x=rsinφcosθ, y=...\n  Jacobi行列式变换"},
    {"id":"int_application","name":"重积分应用",       "group":"重积分",         "desc":"重积分可用于计算曲面面积、重心、转动惯量等物理量。", "methods":"1. 曲面面积：A=∬√(1+f_x²+f_y²)dxdy\n2. 重心：x̄=∬xρdA/∬ρdA\n3. 转动惯量：I=∬r²ρdA"},
    
    # ---- 曲线曲面积分 ----
    {"id":"line_int_1st", "name":"第一型曲线积分",     "group":"曲线曲面积分",   "desc":"对弧长的曲线积分，与曲线方向无关。∫f(x,y)ds", "methods":"1. 参数化：∫f(x(t),y(t))√(x'²+y'²)dt\n2. 几何意义：曲线质量分布\n3. 与方向无关"},
    {"id":"line_int_2nd", "name":"第二型曲线积分",     "group":"曲线曲面积分",   "desc":"对坐标的曲线积分，与方向有关。∫Pdx+Qdy", "methods":"1. 参数化：∫[Px'(t)+Qy'(t)]dt\n2. 与方向有关（反向变号）\n3. 格林公式：∮Pdx+Qdy=∬(Q_x-P_y)dxdy"},
    {"id":"green",        "name":"格林公式",           "group":"曲线曲面积分",   "desc":"建立了闭曲线上的线积分与所围区域上的二重积分的关系。", "methods":"1. ∮Pdx+Qdy = ∬(∂Q/∂x-∂P/∂y)dxdy\n2. 用于计算闭曲线积分\n3. 判断线积分与路径无关：∂Q/∂x=∂P/∂y"},
    {"id":"surface_int",  "name":"曲面积分",           "group":"曲线曲面积分",   "desc":"第一型对面积，第二型对坐标。高斯公式和斯托克斯公式是积分学的顶峰。", "methods":"1. 第一型：∬f(x,y,z)dS\n2. 第二型：∬Pdydz+Qdzdx+Rdxdy\n3. 高斯公式：∭divF dV = ∯F·dS\n4. 斯托克斯公式：∬curlF·dS = ∮F·dr"},
    
    # ---- 无穷级数 ----
    {"id":"num_series",   "name":"数项级数",           "group":"无穷级数",       "desc":"无穷级数∑aₙ是数列求和。收敛性是核心问题。", "methods":"1. 部分和数列收敛⇔级数收敛\n2. 必要条件：aₙ→0\n3. 性质：线性、重排等"},
    {"id":"pos_series",   "name":"正项级数判别法",     "group":"无穷级数",       "desc":"正项级数的收敛性可通过比较、比值、根值等判别法判断。", "methods":"1. 比较判别法：与大敛小散\n2. 比值法：lim aₙ₊₁/aₙ <1收敛\n3. 根值法：lim ⁿ√aₙ <1收敛"},
    {"id":"alt_series",   "name":"一般项级数",         "group":"无穷级数",       "desc":"交错级数用莱布尼茨判别法。绝对收敛和条件收敛的概念。", "methods":"1. 莱布尼茨：单调减→0⇒收敛\n2. 绝对收敛：∑|aₙ|收敛⇒∑aₙ收敛\n3. 条件收敛：自身收敛但绝对值发散"},
    {"id":"power_series", "name":"幂级数",             "group":"无穷级数",       "desc":"∑aₙxⁿ形式。收敛半径R=1/limⁿ√|aₙ|。可逐项求导和积分。", "methods":"1. 收敛半径：R=1/lim|aₙ₊₁/aₙ|\n2. 收敛区间：(-R,R)内绝对收敛\n3. 逐项求导/积分后收敛半径不变"},
    {"id":"taylor_series","name":"函数展开为幂级数",   "group":"无穷级数",       "desc":"将函数展开为泰勒级数或麦克劳林级数。用于近似计算。", "methods":"1. 直接展开：f⁽ⁿ⁾(0)/n!\n2. 间接展开：利用已知展开式\n3. 常用：eˣ=∑xⁿ/n!, sinx=∑(-1)ⁿx²ⁿ⁺¹/(2n+1)!"},
    {"id":"fourier",      "name":"傅里叶级数",         "group":"无穷级数",       "desc":"将周期函数展开为三角级数。傅里叶系数通过正交性计算。", "methods":"1. 傅里叶系数：aₙ=1/π∫f(x)cos(nx)dx\n2. 奇延拓得正弦级数，偶延拓得余弦级数\n3. 收敛定理：狄利克雷条件"},
    
    # ---- 微分方程 ----
    {"id":"ode_basic",    "name":"微分方程概念",       "group":"微分方程",       "desc":"含有未知函数导数的方程。阶数、解、通解、特解是基本概念。", "methods":"1. 阶数：最高阶导数的阶\n2. 通解含任意常数，特解是确定解\n3. 初值问题：给定初始条件求特解"},
    {"id":"ode_first",    "name":"一阶微分方程",       "group":"微分方程",       "desc":"可分离变量、齐次方程、一阶线性方程、全微分方程。", "methods":"1. 可分离：dy/dx=f(x)g(y)\n2. 一阶线性：y'+P(x)y=Q(x)⇒积分因子法\n3. 全微分：∂M/∂y=∂N/∂x"},
    {"id":"ode_high",     "name":"高阶微分方程",       "group":"微分方程",       "desc":"可降阶的高阶方程和线性微分方程解的结构。", "methods":"1. 可降阶：y''=f(x)直接积分\n2. 线性方程：齐次通解+非齐次特解\n3. 常系数齐次：特征方程法"},
    {"id":"ode_const",    "name":"常系数线性微分方程", "group":"微分方程",       "desc":"二阶常系数齐次和非齐次方程的解法。特征根法。", "methods":"1. 齐次解：根的类型决定解的形式\n2. 非齐次：待定系数法（多项式、指数、三角）\n3. 欧拉方程：x²y''+... = 0"},
]

# 构建知识点ID到索引的映射
TOPIC_DICT = {t["id"]: t for t in TOPICS}
TOPIC_IDS = [t["id"] for t in TOPICS]

# 知识图谱中的连接边（同一组内相互连接，跨组也有少数关联边）
def build_edges():
    edges = []
    # 按组内连接
    groups = {}
    for t in TOPICS:
        g = t["group"]
        if g not in groups:
            groups[g] = []
        groups[g].append(t["id"])
    for g, ids in groups.items():
        for i in range(len(ids)-1):
            edges.append((ids[i], ids[i+1]))
        if len(ids) > 2:
            edges.append((ids[0], ids[-1]))
    # 跨组关键连接
    cross = [
        ("function", "seq_limit"), ("function", "derivative"),
        ("seq_limit", "func_limit"), ("func_limit", "continuity"),
        ("continuity", "derivative"), ("derivative", "diff_rules"),
        ("diff_rules", "mean_theorem"), ("mean_theorem", "lhopital"),
        ("mean_theorem", "taylor"), ("taylor", "extremum"),
        ("derivative", "def_integral"), ("def_integral", "indef_integral"),
        ("indef_integral", "substitution"), ("substitution", "by_parts"),
        ("newton_leibniz", "integral_app_area"), ("newton_leibniz", "improper_int"),
        ("vector", "plane_line"), ("plane_line", "surface_curve"),
        ("multi_func", "partial_der"), ("partial_der", "total_diff"),
        ("partial_der", "gradient"), ("gradient", "multi_extremum"),
        ("chain_rule_multi", "partial_der"),
        ("double_int", "triple_int"), ("double_int", "int_application"),
        ("line_int_1st", "line_int_2nd"), ("line_int_2nd", "green"),
        ("green", "surface_int"), ("num_series", "pos_series"),
        ("pos_series", "alt_series"), ("alt_series", "power_series"),
        ("power_series", "taylor_series"), ("taylor_series", "fourier"),
        ("ode_basic", "ode_first"), ("ode_first", "ode_high"),
        ("ode_high", "ode_const"),
    ]
    for a, b in cross:
        if a in TOPIC_DICT and b in TOPIC_DICT:
            edges.append((a, b))
    return edges

EDGES = build_edges()

# ============================================================
# 3. 题目与错误诊断数据
# ============================================================
# 每个知识点配2-3道题，包含数学题和概念题
QUESTIONS = {
    "set": [
        {"q":"区间(0,1)和[0,1]的区别是什么？", "options":["一个有端点一个没有","一个是闭区间一个是开区间","长度不同","没有区别"], "answer":1, "explain":"(0,1)是开区间不含端点，[0,1]是闭区间含端点。"},
        {"q":"集合A={1,2,3}, B={2,3,4}，则A∪B=？", "options":["{1,2,3}","{2,3}","{1,2,3,4}","{1,4}"], "answer":2, "explain":"并集取两个集合的所有元素：{1,2,3,4}"},
    ],
    "function": [
        {"q":"函数f(x)=x²在R上是什么函数？", "options":["单调递增","单调递减","偶函数","奇函数"], "answer":2, "explain":"f(-x)=(-x)²=x²=f(x)，是偶函数。"},
        {"q":"函数f(x)=sin(x)在[0,2π]上有界吗？", "options":["有界","无界","在部分区间有界","不确定"], "answer":0, "explain":"|sin(x)|≤1，所以有界。"},
    ],
    "compfunc": [
        {"q":"f(x)=sin(2x)是复合函数吗？", "options":["是，内层2x外层sin","不是","是，内层sin外层2x","无法判断"], "answer":0, "explain":"复合函数f(g(x))，其中g(x)=2x为内层，sin为外层。"},
    ],
    "seq_limit": [
        {"q":"数列aₙ=1/n，当n→∞时的极限是？", "options":["0","1","不存在","∞"], "answer":0, "explain":"当n→∞时，1/n→0"},
        {"q":"理解题：数列极限ε-N定义中，ε的作用是什么？", "options":["固定一个很小的数","任意正数，用来控制aₙ与A的距离","表示N的大小","表示极限值"], "answer":1, "explain":"∀ε>0，存在N，使得n>N时|aₙ-A|<ε，ε用来控制精度。"},
    ],
    "func_limit": [
        {"q":"lim(x→0) sinx/x = ?", "options":["0","1","不存在","∞"], "answer":1, "explain":"第一个重要极限，结果是1。"},
        {"q":"函数f(x)在x₀处有极限，是否需要f(x₀)有定义？", "options":["必须要有定义","不需要","必须有定义且等于极限值","取决于函数类型"], "answer":1, "explain":"极限与函数在该点的定义无关，只与邻域内的趋近有关。"},
    ],
    "infinity": [
        {"q":"x→0时，sinx与x是等价无穷小吗？", "options":["是","不是","sinx高阶","x高阶"], "answer":0, "explain":"lim(sinx/x)=1，所以是等价无穷小。"},
    ],
    "continuity": [
        {"q":"函数可导一定连续吗？", "options":["一定连续","不一定连续","不一定","取决于函数"], "answer":0, "explain":"可导⇒连续，但连续不一定可导（如|x|在x=0处）"},
        {"q":"f(x)=|x|在x=0处的间断点类型是？", "options":["可去间断点","跳跃间断点","第二类间断点","没有间断，连续"], "answer":3, "explain":"|x|在x=0处连续但不可导。"},
    ],
    "derivative": [
        {"q":"f(x)=x³在x=1处的导数是？", "options":["3","1","0","2"], "answer":0, "explain":"f'(x)=3x²，f'(1)=3"},
        {"q":"理解题：导数f'(x₀)的几何意义是什么？", "options":["函数值","切线斜率","曲线面积","割线长度"], "answer":1, "explain":"导数的几何意义是曲线在x₀处切线的斜率。"},
    ],
    "diff_rules": [
        {"q":"求导：(x²sinx)' = ?", "options":["2x·cosx","2x·sinx + x²·cosx","2x·sinx","x²·cosx"], "answer":1, "explain":"乘积法则：(uv)'=u'v+uv'，即2x·sinx + x²·cosx"},
        {"q":"求导：d/dx[sin(3x+1)] = ?", "options":["cos(3x+1)","3cos(3x+1)","3cos(x)","cos(x)"], "answer":1, "explain":"链式法则：cos(3x+1)·3 = 3cos(3x+1)"},
    ],
    "higher_der": [
        {"q":"f(x)=eˣ的n阶导数是？", "options":["eˣ","neˣ","n!eˣ","0"], "answer":0, "explain":"eˣ的各阶导数都是eˣ。"},
        {"q":"f(x)=sinx的四阶导数是？", "options":["sinx","-sinx","cosx","-cosx"], "answer":0, "explain":"sin'=cos, cos'=-sin, -sin'=-cos, -cos'=sin，四阶导回原函数。"},
    ],
    "implicit_der": [
        {"q":"方程x²+y²=1，求dy/dx", "options":["-x/y","x/y","y/x","-y/x"], "answer":0, "explain":"两边对x求导：2x+2y·y'=0 ⇒ y'=-x/y"},
    ],
    "differential": [
        {"q":"微分dy和增量Δy的关系是？", "options":["dy=Δy","dy≈Δy","dy是Δy的主部","两者无关"], "answer":2, "explain":"dy是Δy的线性主部，dy≈Δy，但dy≠Δy。"},
    ],
    "mean_theorem": [
        {"q":"Rolle定理的三个条件不包括？", "options":["连续","可导","端点值相等","端点值不等"], "answer":3, "explain":"Rolle定理需要：闭区间连续、开区间可导、端点函数值相等。"},
        {"q":"Lagrange中值定理的公式是？", "options":["f(b)-f(a)=f'(ξ)(b-a)","f(b)=f(a)","f'(ξ)=0","f'(ξ)=f(ξ)"], "answer":0, "explain":"拉格朗日中值定理：f(b)-f(a)=f'(ξ)(b-a)，ξ∈(a,b)"},
    ],
    "lhopital": [
        {"q":"洛必达法则适用于哪种极限？", "options":["0/0和∞/∞型","任何类型","0/∞型","1^∞型"], "answer":0, "explain":"洛必达法则只适用于0/0型和∞/∞型不定式。"},
    ],
    "taylor": [
        {"q":"eˣ的麦克劳林展开式是？", "options":["∑xⁿ/n!","∑xⁿ","∑xⁿ/n","∑nxⁿ"], "answer":0, "explain":"eˣ = ∑(n=0→∞) xⁿ/n!"},
    ],
    "extremum": [
        {"q":"f(x)=x³在x=0处是极值吗？", "options":["是极小值","是极大值","不是极值","无法判断"], "answer":2, "explain":"f'(x)=3x²=0，但f''(0)=0，x=0是拐点不是极值点。"},
    ],
    "curve_sketch": [
        {"q":"函数f''(x)>0时，曲线是什么形状？", "options":["凸函数","凹函数","线性","震荡"], "answer":1, "explain":"二阶导大于0 ⇒ 曲线是凹的（concave up）。"},
    ],
    "def_integral": [
        {"q":"定积分∫ₐᵇ f(x)dx的几何意义是？", "options":["曲线下面积","曲线的长度","切线的斜率","函数的平均值"], "answer":0, "explain":"定积分的几何意义是曲线y=f(x)与x轴在[a,b]上围成的面积。"},
    ],
    "indef_integral": [
        {"q":"不定积分∫2x dx = ?", "options":["x²","x²+C","2x+C","x²+1"], "answer":1, "explain":"不定积分要加常数C，∫2x dx = x²+C"},
    ],
    "substitution": [
        {"q":"∫cos(2x)dx用换元法，令u=？", "options":["u=x","u=2x","u=cosx","u=dx"], "answer":1, "explain":"令u=2x，则du=2dx，dx=du/2，∫cosu·du/2 = ½sin(2x)+C"},
    ],
    "by_parts": [
        {"q":"分部积分公式∫udv = ?", "options":["uv-∫vdu","uv+∫vdu","∫vdu","uv"], "answer":0, "explain":"分部积分公式：∫udv = uv - ∫vdu"},
    ],
    "newton_leibniz": [
        {"q":"∫₀¹ x dx = ?", "options":["1/2","1","0","2"], "answer":0, "explain":"原函数x²/2，代入得1/2-0=1/2"},
    ],
    "improper_int": [
        {"q":"广义积分∫₁^∞ 1/x² dx是否收敛？", "options":["收敛于1","发散","收敛于0","收敛于∞"], "answer":0, "explain":"∫₁^R 1/x² dx = 1-1/R →1，收敛。"},
    ],
    "integral_app_area": [
        {"q":"y=x²从0到1围成的面积是？", "options":["1/3","1/2","1","2/3"], "answer":0, "explain":"∫₀¹ x² dx = x³/3|₀¹ = 1/3"},
    ],
    "integral_app_volume": [
        {"q":"y=x在[0,1]绕x轴旋转的体积是？", "options":["π/3","π","2π","π/2"], "answer":0, "explain":"V=π∫₀¹ x² dx = π/3"},
    ],
    "vector": [
        {"q":"向量a=(1,2,3), b=(4,5,6)，则a·b=？", "options":["32","30","28","34"], "answer":0, "explain":"a·b=1×4+2×5+3×6=4+10+18=32"},
        {"q":"向量的数量积（点乘）结果是？", "options":["向量","标量","矩阵","零"], "answer":1, "explain":"数量积的结果是标量（数值）。"},
    ],
    "plane_line": [
        {"q":"平面Ax+By+Cz+D=0的法向量是？", "options":["(A,B,C)","(A,B,D)","(B,C,D)","(A,C,D)"], "answer":0, "explain":"平面方程的法向量就是系数向量(A,B,C)。"},
    ],
    "multi_func": [
        {"q":"z=f(x,y)的图形在三维空间中是什么？", "options":["曲线","曲面","平面","点"], "answer":1, "explain":"二元函数的图形是三维空间中的曲面。"},
    ],
    "partial_der": [
        {"q":"f(x,y)=x²y，求∂f/∂x = ?", "options":["2xy","x²","2y","2x"], "answer":0, "explain":"对x求偏导，y看作常数：∂/∂x(x²y)=2xy"},
    ],
    "total_diff": [
        {"q":"z=x²+y²的全微分dz = ?", "options":["2xdx+2ydy","xdx+ydy","2x+2y","2dx+2dy"], "answer":0, "explain":"∂z/∂x=2x, ∂z/∂y=2y，所以dz=2xdx+2ydy"},
    ],
    "chain_rule_multi": [
        {"q":"z=f(u,v), u=x², v=y，则∂z/∂x = ?", "options":["∂z/∂u·2x","∂z/∂v·2x","∂z/∂u·2x+∂z/∂v·0","∂z/∂u+∂z/∂v"], "answer":0, "explain":"链法则：∂z/∂x = ∂z/∂u·∂u/∂x + ∂z/∂v·∂v/∂x = ∂z/∂u·2x + 0"},
    ],
    "gradient": [
        {"q":"f(x,y)=x²+y²在(1,1)处的梯度是？", "options":["(2,2)","(1,1)","(2,1)","(1,2)"], "answer":0, "explain":"∇f=(2x,2y)，代入(1,1)得(2,2)"},
        {"q":"梯度方向是函数值变化最____的方向？", "options":["快（增长）","慢","平稳","震荡"], "answer":0, "explain":"梯度方向是函数值增长最快的方向。"},
    ],
    "multi_extremum": [
        {"q":"f(x,y)=x²+y²在(0,0)处是？", "options":["极小值","极大值","鞍点","不是极值"], "answer":0, "explain":"f_x=0, f_y=0，判别式AC-B²>0且A>0，是极小值。"},
    ],
    "double_int": [
        {"q":"二重积分∬1 dA的几何意义是？", "options":["区域面积","区域体积","曲线长度","平均值"], "answer":0, "explain":"∬1 dA = 区域D的面积。"},
    ],
    "green": [
        {"q":"格林公式联系了哪两种积分？", "options":["线积分与二重积分","线积分与曲面积分","二重积分与三重积分","曲面积分与三重积分"], "answer":0, "explain":"格林公式将闭曲线上的线积分转化为该曲线所围区域上的二重积分。"},
    ],
    "num_series": [
        {"q":"级数∑1/n是收敛还是发散？", "options":["发散","收敛","条件收敛","不确定"], "answer":0, "explain":"调和级数∑1/n发散。"},
    ],
    "pos_series": [
        {"q":"p级数∑1/n^p，p>1时？", "options":["收敛","发散","不确定","条件收敛"], "answer":0, "explain":"p级数当p>1时收敛，p≤1时发散。"},
    ],
    "power_series": [
        {"q":"幂级数∑xⁿ的收敛半径是？", "options":["1","0","∞","-1"], "answer":0, "explain":"lim|aₙ₊₁/aₙ|=1，收敛半径R=1。"},
    ],
    "taylor_series": [
        {"q":"sinx的麦克劳林级数只包含哪类项？", "options":["奇次项","偶次项","全部项","常数项"], "answer":0, "explain":"sinx是奇函数，展开只有奇次项：∑(-1)ⁿx²ⁿ⁺¹/(2n+1)!"},
    ],
    "ode_first": [
        {"q":"dy/dx = y，该方程的解是？", "options":["y=Ceˣ","y=eˣ+C","y=Cˣ","y=lnx+C"], "answer":0, "explain":"dy/dx=y ⇒ dy/y=dx ⇒ ln|y|=x+C ⇒ y=Ceˣ"},
    ],
    "ode_const": [
        {"q":"y''-3y'+2y=0的特征方程是？", "options":["r²-3r+2=0","r²+3r+2=0","r²-3r-2=0","r²+3r-2=0"], "answer":0, "explain":"特征方程为r²-3r+2=0，解得r=1,2。"},
    ],
}

# 确保每个知识点都有题
for t in TOPICS:
    if t["id"] not in QUESTIONS:
        QUESTIONS[t["id"]] = [
            {"q":f"{t['name']}是高等数学的重要内容，以下说法正确的是？", "options":["说法A：这个知识点很重要","说法B：这个知识点不重要","说法A正确","都不对"], "answer":0, "explain":f"{t['name']}是高等数学的核心内容之一。"},
        ]

# ============================================================
# 4. AI 问答系统（预置知识库）
# ============================================================
QA_KNOWLEDGE = {
    "极限": "极限是高等数学的基础，研究变量趋近某值时的变化趋势。ε-δ语言是极限的严格定义。",
    "导数": "导数是函数的变化率，几何意义是切线斜率。可导必连续。",
    "连续": "函数在某点连续意味着极限值等于函数值。间断点分可去、跳跃、无穷、振荡四类。",
    "积分": "积分是微分的逆运算。定积分求面积，不定积分求原函数。",
    "泰勒": "泰勒公式用多项式逼近函数，是微分学的巅峰成果。",
    "梯度": "梯度∇f指向函数增长最快的方向，方向导数是梯度在特定方向上的投影。",
    "格林": "格林公式将闭曲线积分转化为二重积分，是向量分析的基本定理。",
    "级数": "无穷级数是无限项求和，收敛性是核心问题。",
    "微分方程": "微分方程是包含导数的方程，用于描述变化规律。",
}

def ai_respond(question, topic_name):
    """基于关键词的AI问答系统"""
    q = question.lower()
    answers = {
        "什么是极限": "极限描述当自变量趋近于某值时，函数值无限接近的某个常数。ε-δ语言是其严格定义∀ε>0, ∃δ>0, 0<|x-x₀|<δ ⇒ |f(x)-A|<ε。这是微积分的基础概念。",
        "可导和连续的关系": "可导一定连续，但连续不一定可导。例如f(x)=|x|在x=0处连续但不可导。证明：f'(x₀)存在 ⇒ lim[f(x)-f(x₀)] = f'(x₀)·0 = 0 ⇒ lim f(x) = f(x₀)。",
        "梯度下降": "梯度∇f=(∂f/∂x, ∂f/∂y)指向函数增长最快的方向。梯度下降法用负梯度方向更新参数：xₙ₊₁=xₙ-α∇f(xₙ)，α是学习率。这是机器学习最核心的优化算法。",
        "泰勒公式": "泰勒公式：f(x)=∑f⁽ᵏ⁾(x₀)/k!·(x-x₀)ᵏ+Rₙ(x)，用多项式逼近函数。麦克劳林公式是x₀=0的特例。",
    }
    for key, ans in answers.items():
        if key in q:
            return ans, "概念理解类"
    # 通用回答
    return f"关于「{topic_name}」中的这个问题，这属于概念理解类问题。建议你可以先复习{topic_name}的基本定义和核心定理，然后做一些基础题巩固理解。要不要试试这个知识点下的练习？", "概念理解类"

# ============================================================
# 5. 知识图谱布局（固定位置保证每次一致）
# ============================================================
def compute_layout():
    """为每个知识点计算在图谱中的位置"""
    pos = {}
    groups = {}
    for t in TOPICS:
        g = t["group"]
        if g not in groups:
            groups[g] = []
        groups[g].append(t["id"])
    
    group_list = list(groups.keys())
    n_groups = len(group_list)
    
    for gi, g in enumerate(group_list):
        ids = groups[g]
        n = len(ids)
        # 每个组在一个扇形区域内分布
        center_angle = gi / n_groups * 2 * np.pi
        radius = 3
        cx = radius * np.cos(center_angle)
        cy = radius * np.sin(center_angle)
        
        for i, tid in enumerate(ids):
            if n == 1:
                angle = center_angle
                r = 0.5
            else:
                spread = 0.8
                angle_offset = (i / (n-1) - 0.5) * spread if n > 1 else 0
                angle = center_angle + angle_offset
                r = 0.5 + 0.3 * (i % 3)
            x = cx + r * np.cos(angle + np.pi/2)
            y = cy + r * np.sin(angle + np.pi/2)
            pos[tid] = (x, y)
    return pos

LAYOUT_POS = compute_layout()

# ============================================================
# 6. 绘制知识图谱（Plotly）
# ============================================================
def build_knowledge_graph():
    """构建Plotly知识图谱"""
    # 边
    edge_traces = []
    for a, b in EDGES:
        if a in LAYOUT_POS and b in LAYOUT_POS:
            x0, y0 = LAYOUT_POS[a]
            x1, y1 = LAYOUT_POS[b]
            edge_traces.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                mode='lines',
                line=dict(width=1.5, color='#888'),
                hoverinfo='none',
                showlegend=False
            ))
    
    # 节点
    node_x, node_y, node_text, node_colors, node_ids, node_sizes = [], [], [], [], [], []
    for t in TOPICS:
        tid = t["id"]
        x, y = LAYOUT_POS[tid]
        node_x.append(x)
        node_y.append(y)
        node_text.append(t["name"])
        node_ids.append(tid)
        color = GROUP_COLORS.get(t["group"], "#AAAAAA")
        node_colors.append(color)
        # 已被访问/打分的节点更大
        if tid in st.session_state.ratings:
            node_sizes.append(20)
        else:
            node_sizes.append(14)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        textfont=dict(size=10, color='#333'),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white'),
            symbol='circle'
        ),
        customdata=node_ids,
        hovertemplate='<b>%{text}</b><extra></extra>',
        showlegend=False
    )
    
    fig = go.Figure(data=edge_traces + [node_trace])
    
    fig.update_layout(
        title=None,
        showlegend=False,
        hovermode='closest',
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=550,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        clickmode='event+select',
    )
    
    # 添加组图例（固定位置）
    group_items = list(GROUP_COLORS.items())
    # 在图上添加图例标注
    for i, (gname, gcolor) in enumerate(group_items):
        # 放在右侧浮动位置
        fig.add_annotation(
            x=6.5, y=3.8 - i * 0.4,
            text=f"● {gname}",
            font=dict(size=11, color=gcolor),
            showarrow=False,
            xanchor='left',
            yanchor='middle',
        )
    
    return fig

# ============================================================
# 7. 详情页：知识点学习页面
# ============================================================
def render_detail_page(topic_id):
    topic = TOPIC_DICT[topic_id]
    st.markdown(f"# 📖 {topic['name']}")
    
    # ---- 标记已访问 ----
    if topic_id not in st.session_state.history:
        st.session_state.history[topic_id] = {"visited": True, "correct": 0, "wrong": 0, "qas": []}
    else:
        st.session_state.history[topic_id]["visited"] = True
    
    # ---- 返回按钮 ----
    if st.button("← 返回知识图谱"):
        st.session_state.page = "home"
        st.rerun()
    
    # ---- 区块1: AI讲解 ----
    st.markdown("---")
    st.markdown("## 🤖 AI 作为讲解者")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### 📌 知识点阐述")
        st.info(topic["desc"])
    with col2:
        st.markdown("### 🛠️ 核心方法")
        st.success(topic["methods"])
    
    # ---- 区块2: AI提问 ----
    st.markdown("---")
    st.markdown("## ❓ AI 作为提问者")
    
    qs = QUESTIONS.get(topic_id, [])
    if qs:
        # 随机选一道题（记录当前题目索引）
        if f"q_index_{topic_id}" not in st.session_state:
            st.session_state[f"q_index_{topic_id}"] = 0
        if f"q_answered_{topic_id}" not in st.session_state:
            st.session_state[f"q_answered_{topic_id}"] = False
        if f"q_feedback_{topic_id}" not in st.session_state:
            st.session_state[f"q_feedback_{topic_id}"] = ""
        
        q_idx = st.session_state[f"q_index_{topic_id}"]
        current_q = qs[q_idx % len(qs)]
        
        st.markdown(f"**第{q_idx % len(qs)+1}题：{current_q['q']}**")
        
        # 显示选项
        opts = current_q["options"]
        selected = st.radio("选择你的答案：", opts, key=f"q_radio_{topic_id}_{q_idx}", index=None)
        
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("提交答案", key=f"submit_{topic_id}_{q_idx}"):
                if selected is None:
                    st.warning("请先选择一个答案")
                else:
                    opt_idx = opts.index(selected)
                    if opt_idx == current_q["answer"]:
                        st.success("✅ 回答正确！")
                        st.session_state.history[topic_id]["correct"] += 1
                        st.session_state[f"q_feedback_{topic_id}"] = "正确"
                    else:
                        correct_opt = opts[current_q["answer"]]
                        # 错误类型诊断
                        st.error("❌ 回答错误")
                        st.info(f"💡 {current_q['explain']}")
                        st.session_state.history[topic_id]["wrong"] += 1
                        st.session_state[f"q_feedback_{topic_id}"] = f"错误，正确答案是：{correct_opt}"
                    st.session_state[f"q_answered_{topic_id}"] = True
        
        with col_b:
            if st.session_state[f"q_answered_{topic_id}"]:
                if st.button("下一题 →", key=f"next_{topic_id}_{q_idx}"):
                    st.session_state[f"q_index_{topic_id}"] = (q_idx + 1) % len(qs)
                    st.session_state[f"q_answered_{topic_id}"] = False
                    st.session_state[f"q_feedback_{topic_id}"] = ""
                    st.rerun()
        
        # 显示上次反馈
        if st.session_state[f"q_feedback_{topic_id}"]:
            st.markdown(f"**上题反馈**：{st.session_state[f'q_feedback_{topic_id}']}")
    
    st.markdown("*提示：除了选择题，还可以思考：这个知识点的核心思想是什么？它与其他知识点有什么联系？*")
    
    # ---- 区块3: 五星打分 ----
    st.markdown("---")
    st.markdown("## ⭐ 自我评估打分")
    st.markdown("你觉得这个知识点掌握了多少？点击星星打分：")
    
    current_rating = st.session_state.ratings.get(topic_id, 0)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            star_label = "⭐" if i < current_rating else "☆"
            if st.button(star_label, key=f"star_{topic_id}_{i}"):
                st.session_state.ratings[topic_id] = i + 1
                st.rerun()
    
    st.markdown(f"**目前评分：{'⭐' * current_rating}{'☆' * (5 - current_rating)} ({current_rating}/5)**")
    
    # ---- 区块4: 提问环节 ----
    st.markdown("---")
    st.markdown("## 💬 向AI提问")
    user_q = st.text_input("输入你对这个知识点的疑问：", key=f"qa_input_{topic_id}")
    if st.button("提问", key=f"qa_btn_{topic_id}"):
        if user_q.strip():
            answer, q_type = ai_respond(user_q, topic["name"])
            st.markdown(f"**🤖 AI回答**：{answer}")
            st.info(f"📂 问题类型：{q_type}")
            if st.button("好，去刷这个知识点的题", key=f"qa_goto_{topic_id}"):
                st.session_state[f"q_index_{topic_id}"] = 0
                st.session_state[f"q_answered_{topic_id}"] = False
                st.rerun()
            # 记录问答
            st.session_state.history[topic_id]["qas"].append({"q": user_q, "type": q_type})
        else:
            st.warning("请输入问题内容")

# ============================================================
# 8. 规划页面
# ============================================================
def render_planning_page():
    st.markdown("# 🧭 学习规划中心")
    
    if st.button("← 返回知识图谱"):
        st.session_state.page = "home"
        st.rerun()
    
    # 检查是否有学习记录
    visited_topics = {tid: info for tid, info in st.session_state.history.items() if info["visited"]}
    
    if not visited_topics:
        st.info("📌 你还没有学习任何知识点。请先回到知识图谱，点击学习！")
        return
    
    # ---- 历史记录 ----
    st.markdown("## 📊 学习历史记录")
    st.markdown(f"已学习 **{len(visited_topics)}** 个知识点")
    
    records = []
    for tid, info in visited_topics.items():
        t = TOPIC_DICT.get(tid)
        if t is None:
            continue
        rating = st.session_state.ratings.get(tid, 0)
        total_q = info["correct"] + info["wrong"]
        acc = f"{info['correct']}/{total_q}" if total_q > 0 else "未做题"
        records.append({
            "知识点": t["name"],
            "组": t["group"],
            "自评": "⭐" * rating + "☆" * (5 - rating),
            "答题情况": acc,
            "提问数": len(info["qas"]),
            "tid": tid
        })
    
    if records:
        st.table([{"知识点": r["知识点"], "组": r["组"], "自评": r["自评"], "答题正确": r["答题情况"], "提问数": r["提问数"]} for r in records])
    
    # ---- 动态规划 ----
    st.markdown("---")
    st.markdown("## 🎯 动态学习规划")
    
    # 找到最推荐学习/复习的知识点
    # 策略：优先推荐低分且少练习的；其次推荐未学习的强关联知识点
    recommendations = []
    for t in TOPICS:
        tid = t["id"]
        rating = st.session_state.ratings.get(tid, 0)
        info = st.session_state.history.get(tid, {"visited": False, "correct": 0, "wrong": 0})
        total_q = info["correct"] + info["wrong"]
        wrong = info["wrong"]
        
        if not info["visited"]:
            # 未学习但相关联 - 推荐优先级中等
            recommendations.append((tid, 2, "未学"))
        elif rating < 3 or (total_q > 0 and wrong / total_q > 0.5):
            # 低分或高错误率 - 需要复习
            priority = 10 - rating + wrong
            recommendations.append((tid, priority, "需复习"))
        elif rating >= 4 and total_q >= 2:
            # 掌握较好 - 可以继续进阶
            recommendations.append((tid, 1, "已掌握"))
        else:
            # 中等
            recommendations.append((tid, 3, "可巩固"))
    
    # 按优先级排序
    recommendations.sort(key=lambda x: -x[1])
    
    st.markdown("### 🥇 最推荐的下一步")
    if recommendations:
        top3 = recommendations[:5]
        for i, (tid, priority, status) in enumerate(top3):
            t = TOPIC_DICT[tid]
            color = GROUP_COLORS.get(t["group"], "#333")
            st.markdown(f"{'🔴' if status=='需复习' else '🟡' if status=='未学' else '🟢'} **{i+1}. {t['name']}**（{t['group']}）— **{status}**")
            if status == "需复习":
                st.caption(f"建议：返回该知识点重新学习，你的自评仅{st.session_state.ratings.get(tid, 0)}⭐，且错题较多。")
            elif status == "未学":
                st.caption(f"建议：学习这个新知识点，它与已学内容有紧密关联。")
            else:
                st.caption(f"建议：巩固练习，尝试更难的综合题。")
            
            if st.button(f"去学习「{t['name']}」", key=f"rec_{tid}"):
                st.session_state.selected_topic = tid
                st.session_state.page = "detail"
                st.rerun()
    
    # 学习建议总结
    st.markdown("---")
    st.markdown("### 📝 综合学习建议")
    need_review = [r for r in recommendations if r[2] == "需复习"]
    not_learned = [r for r in recommendations if r[2] == "未学"]
    
    if need_review:
        st.warning(f"有 **{len(need_review)}** 个知识点需要复习，建议优先巩固薄弱环节。")
    if not_learned:
        st.info(f"还有 **{len(not_learned)}** 个知识点未学习，学完当前内容后按计划推进。")

# ============================================================
# 9. 主页：知识图谱 + 搜索 + 快速入口
# ============================================================
def render_home_page():
    # ---- 标题 ----
    st.markdown("<h1 style='text-align:center; color:#2c3e50;'>📐 MathTutor 高等数学学习可视化教学平台</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#7f8c8d; font-size:18px;'>按认知风格自适应的个性化学习助手 | 覆盖高数上下册13章核心内容</p>", unsafe_allow_html=True)
    
    # ---- 图例标注栏 ----
    st.markdown("### 🎨 色彩图例")
    col_legend = st.columns(6)
    group_items = list(GROUP_COLORS.items())
    for i, (gname, gcolor) in enumerate(group_items):
        with col_legend[i % 6]:
            st.markdown(f"<span style='color:{gcolor}; font-size:20px;'>●</span> {gname}", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ---- 搜索栏 ----
    search_val = st.text_input("🔍 搜索知识点（输入名称关键词，如'极限'、'导数'、'积分'）：",
                               value=st.session_state.search_query, key="search_input")
    if search_val != st.session_state.search_query:
        st.session_state.search_query = search_val
    
    # ---- 知识图谱 ----
    st.markdown("### 🗺️ 知识图谱（点击圆圈进入学习）")
    fig = build_knowledge_graph()
    
    # 处理点击事件 - 使用plotly的点击回调
    # 我们通过检测点击事件并重定向
    event = st.plotly_chart(fig, use_container_width=True, key="knowledge_graph", on_select="rerun")
    
    # 处理点击
    if event and "selection" in event and event["selection"] and "points" in event["selection"]:
        points = event["selection"]["points"]
        if points and "customdata" in points[0]:
            tid = points[0]["customdata"]
            if tid in TOPIC_DICT:
                st.session_state.selected_topic = tid
                st.session_state.page = "detail"
                st.rerun()
    
    # ---- 搜索匹配跳转 ----
    if st.session_state.search_query:
        query = st.session_state.search_query.lower()
        matched = [t for t in TOPICS if query in t["name"].lower() or query in t["group"].lower()]
        if matched:
            st.markdown(f"**搜索结果（{len(matched)}个匹配）**：")
            for t in matched[:5]:
                color = GROUP_COLORS.get(t["group"], "#333")
                btn_label = f"{t['name']}（{t['group']}）"
                if st.button(btn_label, key=f"search_{t['id']}"):
                    st.session_state.selected_topic = t["id"]
                    st.session_state.page = "detail"
                    st.rerun()
        else:
            st.info("未找到匹配的知识点，试试其他关键词。")
    
    # ---- 知识点快速入口列表 ----
    st.markdown("---")
    st.markdown("### 📋 全部知识点（点击名称进入学习）")
    
    # 按组分开展示
    groups = {}
    for t in TOPICS:
        g = t["group"]
        if g not in groups:
            groups[g] = []
        groups[g].append(t)
    
    tabs = st.tabs(list(groups.keys()))
    for i, (gname, topics) in enumerate(groups.items()):
        with tabs[i]:
            for t in topics:
                tid = t["id"]
                rating = st.session_state.ratings.get(tid, 0)
                star_str = "⭐" * rating + "☆" * (5 - rating) if rating > 0 else "未评分"
                color = GROUP_COLORS.get(gname, "#333")
                if st.button(f"● {t['name']}  {star_str}", key=f"list_{tid}"):
                    st.session_state.selected_topic = tid
                    st.session_state.page = "detail"
                    st.rerun()
    
    # ---- 规划入口 ----
    st.markdown("---")
    st.markdown("### 🧭 学习规划")
    visited_count = sum(1 for v in st.session_state.history.values() if v["visited"])
    if visited_count > 0:
        st.success(f"已学习 {visited_count} 个知识点，点击进入规划中心查看详细分析和推荐。")
        if st.button("进入学习规划中心 →", use_container_width=True):
            st.session_state.page = "planning"
            st.rerun()
    else:
        st.info("开始学习吧！点击上面的知识图谱中的圆圈，进入第一个知识点。")

# ============================================================
# 10. 主入口
# ============================================================
def main():
    if st.session_state.page == "home":
        render_home_page()
    elif st.session_state.page == "detail":
        if st.session_state.selected_topic and st.session_state.selected_topic in TOPIC_DICT:
            render_detail_page(st.session_state.selected_topic)
        else:
            st.error("知识点不存在，返回首页")
            st.session_state.page = "home"
            st.rerun()
    elif st.session_state.page == "planning":
        render_planning_page()
    else:
        st.session_state.page = "home"
        st.rerun()

if __name__ == "__main__":
    main()
