set terminal postscript eps color solid "Helvetica" 24
set output "runs/score_graph.eps"
set title "RL Episode Score Graph"
set style data lines
set key on bmargin horizontal
set border 3
set xtics nomirror
set ytics nomirror
set multiplot

set xrange[-0.5:100]
set xlabel "Episode Number"

set yrange[0:64]
set ylabel "Final Score"

set datafile separator ","
plot "runs/bravo/results.csv" using 1:3 title "Bravo", \
	"runs/charlie/results.csv" using 1:3 title "Charlie", \
	"runs/delta/results.csv" using 1:3 title "Delta", \
	"runs/echo/results.csv" using 1:3 title "Echo", \
	"runs/foxtrot/results.csv" using 1:3 title "Foxtrot"

