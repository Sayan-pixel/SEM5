# Part D: Comparison and analysis

## 1. Overlay the three throughput curves
The curves have been generated and saved as `comparison.png` in the current directory. The graph visually compares the throughput $S$ against the offered load $G$ for Pure Aloha, Slotted Aloha, and 1-persistent CSMA (a=0.01).

## 2. Why the Aloha curves collapse at high load while the CSMA curve does not
In Pure and Slotted Aloha, stations transmit completely blindly. As the offered load ($G$) increases, the probability of two or more frames overlapping increases exponentially. Because every transmission is uncoordinated, a high $G$ leads to almost every frame experiencing a collision, causing the throughput to collapse towards zero.

In contrast, 1-persistent CSMA uses carrier sensing (listen before talk). If the channel is busy, stations defer their transmissions. This prevents the chaotic, overlapping transmissions that plague Aloha at high loads. Even when $G$ is very high, collisions only happen when multiple stations start transmitting within the small vulnerable window ($a$). Thus, CSMA sustains a relatively high throughput because it effectively serializes most of the traffic and prevents most potential collisions before they occur.

## 3. The single quantity that controls how close CSMA comes to full utilization
The single quantity is the **propagation delay ($a$)**, which defines the vulnerable window. 

By rerunning the simulation with different values of $a$, we observe the following peaks:
* **$a = 0.01$**: Peak $S \approx 0.527$ at $G = 0.90$
* **$a = 0.05$**: Peak $S \approx 0.497$ at $G = 1.00$
* **$a = 0.10$**: Peak $S \approx 0.452$ at $G = 0.90$

As the propagation delay $a$ (and consequently the vulnerable window) grows, the peak throughput drops. This happens because a larger $a$ means it takes longer for a station's transmission to be "heard" by others, increasing the chance that another station will sense the channel as idle and initiate a colliding transmission.

## 4. State the vulnerable window of each protocol and connect it to the height of each peak
The vulnerable window is the period during which another transmission starting will cause a collision:
* **Pure Aloha**: Two frame-times ($2$). Since it has the largest vulnerable window, it suffers the most collisions, resulting in the lowest peak throughput ($\approx 0.18$).
* **Slotted Aloha**: One frame-time ($1$). Because slotting eliminates partial overlaps, the vulnerable window is halved compared to Pure Aloha. This exactly doubles the peak throughput ($\approx 0.37$).
* **1-persistent CSMA**: One propagation delay ($a$). Since $a$ is very small (e.g., $0.01$ frame-times), the vulnerable window is tiny. This drastically reduces collisions, allowing the peak throughput to climb far higher than both Aloha variants ($\approx 0.53$ for $a=0.01$).
