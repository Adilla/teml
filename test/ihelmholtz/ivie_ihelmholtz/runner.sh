n_values=(3 17 33)
m_values=(8 750 7500)

for meshsize in "${m_values[@]}"
do 
    echo $meshsize
    for datasize in "${n_values[@]}"
    do 
	echo $datasize
	#echo "Sequential Helmholtz"
	#srun -p haswell64 ./ihelmholtz $meshsize $datasize
	#echo "Parallel helmholtz outermost"
	#srun -p haswell64 -c 24 ./ihelmholtz_layout1 $meshsize $datasize 
	#echo "Parallel helmholtz outermost + inner"
	#srun -p haswell64 -c 24 ./ihelmholtz_layout1_fuse $meshsize $datasize 
	#echo "Parallel helmholtz comp1"
	#srun -p haswell64 -c 24 ./ihelmholtz_layout2 $meshsize $datasize 
	#echo "Parallel helmholtz comp2 outermost"
	#srun -p haswell64 -c 24 ./ihelmholtz_layout2_fuse $meshsize $datasize 
	#echo "Parallel helmholtz comp2 outermost + inner"
	#srun -p haswell64 -c 24 ./ihelmholtz_layout3 $meshsize $datasize 
	#echo "Parallel helmholtz comp3"
	#srun -p haswell64 -c 24 ./ihelmholtz_layout3_fuse $meshsize $datasize 
	echo "Parallel Pluto"
	srun -p haswell64 -c 24 ./ihelmholtz.pluto_p $meshsize $datasize 
	#echo "Parallel Pluto no fuse"
	#srun -p haswell64 -c 24 ./ihelmholtz.pluto_pf0 $meshsize $datasize 
	#echo "Parallel Pluto smart fuse"
	#srun -p haswell64 -c 24 ./ihelmholtz.pluto_pf1 $meshsize $datasize 
	#echo "Parallel Pluto max fuse"
	#srun -p haswell64 -c 24 ./ihelmholtz.pluto_pf2 $meshsize $datasize 
	echo "Parallel Pluto tile no fuse"
	srun -p haswell64 -c 24 ./ihelmholtz.pluto_pf0t $meshsize $datasize 
	echo "Parallel Pluto tile smart fuse"
	srun -p haswell64 -c 24 ./ihelmholtz.pluto_pf1t $meshsize $datasize 
	echo "Parallel Pluto tile max fuse"
	srun -p haswell64 -c 24 ./ihelmholtz.pluto_pf2t $meshsize $datasize 
 
		
  done
done
