(define (problem BW-generalization-4)
(:domain blocksworld-4ops)(:objects i f e j h)
(:init 
(handempty)
(ontable i)
(ontable f)
(ontable e)
(ontable j)
(ontable h)
(clear i)
(clear f)
(clear e)
(clear j)
(clear h)
)
(:goal
(and
(on i f)
(on f e)
(on e j)
(on j h)
)))