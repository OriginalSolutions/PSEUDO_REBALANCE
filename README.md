# PSEUDO_REBALANCE
---
BACKTESTING
---

The project is a development of: the author's idea based on the mechanism of "negative price correlation".

The project is used to run backtest using (the among other things) library:
"pandas" in order to accelerate the calculations performed 
and "request" used to send a request in rest api technology to retrieve prices.

The project takes into account the idea that "the portfolio is not balanced".

For example:
When the price of the first token went up, we sell only part of its profit.
We then invest that profit in the token whose price went down.
This means that the portfolio after the changes may have an asymmetrical value of assets, for example: 45%/55%.

The value curve of a portfolio using the "oscillate around the level of the contractual profit distribution" algorithm can be treated as an oscillator for the value curve of a portfolio not using this algorithm.

In other words:
You can use these deviations to build a signaler that generates buy or sell signals for a static portfolio - not using "pseudo-balancing"

Project tested only on the "gate" exchange.
