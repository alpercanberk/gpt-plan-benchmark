(define (problem BW-generalization-4)
(:domain blocksworld-4ops)(:objects c d b h l g f k)
(:init 
(handempty)
(ontable c)
(ontable d)
(ontable b)
(ontable h)
(ontable l)
(ontable g)
(ontable f)
(ontable k)
(clear c)
(clear d)
(clear b)
(clear h)
(clear l)
(clear g)
(clear f)
(clear k)
)
(:goal
(and
(on c d)
(on d b)
(on b h)
(on h l)
(on l g)
(on g f)
(on f k)
)))