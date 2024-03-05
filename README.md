# 🏭 Measuring Industrial Agglomeration

Traditionally, industrial agglomeration is measured using a metric called Location Quotient (LQ). This metric is simple but has its limits. For example, less populated and remote counties will sometimes have high LQs, despite having low employment counts. This paper proposes a new metric to resolve these issues called Proximity Adjusted Location Quotients (PA-LQ or CLQ).

<p align="center">
  <img src="src\assets\images\map_image.png" alt="Map Selection" width="100%"/>
</p>

In this demo, you can explore LQs and CLQs for different industries and counties and notice the differences in the results.

## How to use

1. Download the "Proximity-Adjusted LQ.csv" dataset from [here](https://www.statsamerica.org/downloads/Proximity-Adjusted-LQ.zip).
2. Place "Proximity-Adjusted LQ.csv" in ./data.
3. Install requirements using: `pip install -r requirements.txt`
4. Run src/main.py (`python src/main.py`).
