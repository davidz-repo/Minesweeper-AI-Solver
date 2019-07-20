## Minesweeper Solver

**Qixiang (David) Zhang**

#### AI Agent's Methods
First explore the 3x3 grid method - uncover all the surrounding tiles if the center percept is 0 (***the Patient 0***). The method can uncover all the tiles that surrounds 0. Then, look at all the percept tiles that are 1. If all the explored tiles surrounding the 1 are not a mine, and only 1 tile is unexplored surrounding the 1, then this tile must be a mine. Applying this logic, the algorithm is able to score perfectly given the "supereasy" world.

1. ***The 3x3 algorithm***: The percept number tells how many mines exactly there are around the tile (maximum of 8 and minimum of 0). In other words, the rest of the neighbors cannot be mines.
2. ***Multi-square algorithm***: The 3x3 algorithm fails when the unexplored tiles is more than the number of mines within these unexplored tiles. By looking at multiple different squares at once, similar deduction can be made. For example, if from percept X - there is a mine in one of A, B, C, and D, and from percept Y, there is a mine in one of A and B, then C and D must be safe.
3. ***Gaussian Elimination***: This algorithm is the extension of the multis-square algorithm. Instead of looking at one specific frontier tile, the algorithm looks at all the unexplored tiles. It creates a matrix - the each column is an unexplored tile (variables); the last column would be the percepts (constraints). Solving the matrix would give us the solution for each tile whether safe or not. First half of the algorithm only reduce the matrix to row echelon form. The second uses the condition that the tile can only be binary (mine or not a mine) to further simplify the matrix.
4. ***Guessing***: Since minesweeper is NP-complete, this algorithm is very important. Every unexplored tiles can be either neighboring a percept or not. The algorithm first assigns an unexplored tile with the probability of being a mine using $\frac{total\space mines\space left}{total\space unexplored\space tiles}$. Then, it calculates the probability using the percepts for those near an already discovered tiles. The algorithm assign each unexplored tile with the highest probabilities among all the calculations. Then, the algorithm pick the tile with the smallest probability to assume it is safe to uncover. If there are more than one tiles with the same probabilities, it picks one randomly.

**Note**: refer to [MyAI](Minesweeper_Python/src/MyAI.py) for details on the algorithm

#### Performance
|Board Size|Sample Size|Score|Worlds Complete|Percentage|
|-|-|-|-|-|
|5x5             |2000|2000|2000|100.0 %|
|8x8             |2000|1737|1737| 86.9 %|
|16x16           |2000|1650|1650| 82.5 %|
|16x30           |2000|2010|670 |33.5 %|
|Total Summary   |8000|9047|6057 |75.7 %|

**Reference:**  
- Li, Bai. *"How to Write your own Minesweeper AI"*. "Lucky's Notes". *Worldpress*. December 23, 2012. Web. September 27, 2018. [link](https://luckytoilet.wordpress.com/2012/12/23/2125/)  
- Massaioli, Robert. *"Solving Minesweeper with Matrices"*. "Programming by Robert Massaioli". *Worldpress*. January 12, 2013. Web. November 25, 2018. [link](https://massaioli.wordpress.com/2013/01/12/solving-minesweeper-with-matricies/comment-page-1/)  
- Studholme, Chris. *"Minesweeper as a Constraint Satisfaction Problem
"*. [link](http://www.cs.toronto.edu/~cvs/minesweeper/minesweeper.pdf)
