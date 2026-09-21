import pygame

pygame.init()

WIDTH =800
HEIGHT=600

screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Trace Game")

running = True

points =[(100,300)]

redo_points=[]

wall = pygame.Rect(300,200,200,50)

failed_line = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button ==1:
                start = points[-1]
                end=event.pos
                if wall.clipline(start,end):
                    failed_line=(start,end)
                else:
                    points.append(end)
                    redo_points.clear()
                    failed_line=None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and event.mod & pygame.KMOD_CTRL:
                if len(points)>1:
                    redo_points.append(points.pop())
            if event.key == pygame.K_y and event.mod & pygame.KMOD_CTRL:
                if redo_points:
                    points.append(redo_points.pop())

    screen.fill("black")

    if len(points)>=2:
        pygame.draw.lines(screen,"white",False,points,3)
        if failed_line:
            pygame.draw.line(screen,"red",failed_line[0],failed_line[1],3)

    pygame.draw.rect(screen,"grey",wall)

    pygame.draw.circle(screen,"green",(100,300),20)
    pygame.draw.circle(screen,"red",(700,300),20)

    pygame.display.flip()

pygame.quit()