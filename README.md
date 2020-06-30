# MT5 Trading Tool
A GUI-based calculator for Forex trading using the MT5 platform. It currently includes the following functions:
- Entry and execution of a trade order 
  - Includes entry of a stop loss, takeprofit, percentage risk, deviation and entry price for pending orders
- A function that automatically sets the take profit to be a desired risk : reward ratio
- Placement of pending orders including Buy / Sell limits and stops
- An automatic calculation of volume based on the chosen risk, the entered stop loss and entry price
- Ability to open a double order instantly
- Functions that return both open positions and pending orders respectively
- The ability to instantly close all open positions in their entirety 
- The ability to close half or a desired percentage of open positions. This will soon take a position ID as input to select a single position to enact these changes
- Instantly cancel all pending orders or select a specific order to cancel via its position ID
- A function to halve the risk of an order
- A 'runner' function that instantly sets the stop loss a few points above break even, it closes 80% of the open position and increases the take profit level
- Auto break even function sets an orders stop loss a few points above the inital entry price. Currently not 'automatic'

--------------------------------------------------------------------------------------

<h2>Potential Future Functionality</h2>
 I am looking to add some automatic functions that screen the prices and act accordingly. This includes implementation of a partial take profit which will be used to either close a desired percentage of the posititon, begin a runner or even just automatically go to break even once this partial TP is met.
 
 I also need to fully implement the selection of a position ID for the corresponding functions. 
