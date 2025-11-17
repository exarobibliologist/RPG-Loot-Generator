# RPG Loot Drop Generator
This Python tool has two main features: 1) the customizable loot drop chart with 100 rows on the left side of the screen, and a simple random number generator that generates pieces of loot per click.

## To Use
* Fill in the chart with loot.
Prefix with WEIGHT: for weighting.
Use {XdY} (dice) or {Min-Max} (range) for dynamic values.

For example, in the list

100: Swords
{1d1000} Coins
{42-69} Antique Coins

Swords will be 100x more likely to appear in the generated list, you will get a random amount of coins determined as if you had rolled a d1000, and you would get a fixed (between 42-69) random amount of antique coins.

This list will be saved when you close the app, so you can reuse it again and again.

* Click the button in the middle marked "Generate Loot"

It's that simple!

![Preview Picture](https://i.imgur.com/BSIlRMz.png)