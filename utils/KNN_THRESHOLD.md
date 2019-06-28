# 阈值对KNN搜索结果的影响

# How threshold affects KNN searching result

下面的表格显示了阈值和聚类人数之间的关系。

The table below shows the relationship between threshold and number of people of face grouping.

| Threshold | number of people | number of image in each person |
| :--: | :--: | :--: |
| 阈值 | 总人数 | 每个人所拥有的图片数 |
| ground truth | 5 | 36,31,28,5,3 |
| 0.6 | 1 | all |
| 0.5 | 3 | 59,27,7 |
| 0.4 | 4 | 56,30,4,3 |
| 0.3 | 6 | 32,26,26,4,3,2 |
| 0.2 | 16 | 28,24,20,4,3,3,2,1...1 |

从表中我们可以看出，随着阈值的降低，聚类人数越来越多。当阈值在0.3左右时，有着最好的聚类效果。

From the table, we can conclude that the number of people increases as the threshold decreases. With the threshold of 0.3, we can get the best result.
