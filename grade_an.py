import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 读取CSV文件
df = pd.read_csv("d:\\repos\\py_t\\grade.csv")

# 计算总分的五分一段表
total_score_bins = pd.cut(df["初试总分"], bins=range(340, 420, 5))
total_score_distribution = df.groupby(total_score_bins).size()

# 计算各科分数的最高最低值
subject_columns = ["政治", "外国语", "业务课一", "业务课二"]
subject_stats = df[subject_columns].agg(["max", "min"])

# 计算各科分数的五分一段表
subject_distributions = {}
for subject in subject_columns:
    bins = pd.cut(df[subject], bins=range(50, 150, 5))
    distribution = df.groupby(bins).size()
    subject_distributions[subject] = distribution

# 分析两门业务课成绩的相关性
correlation = df["业务课一"].corr(df["业务课二"])
print(f"业务课一与业务课二的相关系数: {correlation}")

# 绘制散点图
sns.scatterplot(x="业务课一", y="业务课二", data=df)
plt.title("业务课一与业务课二的散点图")
plt.xlabel("业务课一")
plt.ylabel("业务课二")
plt.show()

# 输出结果
print("总分的五分一段表:")
print(total_score_distribution)
print("\n各科分数的最高最低值:")
print(subject_stats)
print("\n各科分数的五分一段表:")
for subject, distribution in subject_distributions.items():
    print(f"\n{subject}的五分一段表:")
    print(distribution)
