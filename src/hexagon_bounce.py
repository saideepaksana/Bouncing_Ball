import sys, math, random, pygame
from pygame import Vector2

# ---------- Config ----------
WIDTH, HEIGHT = 800, 600
FPS = 60

BG_COLOR = (255, 255, 255)

# Ball
BALL_RADIUS = 10
BALL_COLOR = (128, 0, 128)      # purple
BALL_OUTLINE = (238, 130, 238)  # violet
ball_pos = Vector2(WIDTH/2 + 100, HEIGHT/2)
ball_vel = Vector2(200, -50)     # initial push
GRAVITY = Vector2(0, 500)        # pixels/sec² downward

# Hexagon
HEX_CENTER = Vector2(WIDTH/2, HEIGHT/2)
HEX_RADIUS = 250
ROT_SPEED = math.radians(20)     # 20° per second

# Sparks
SPARK_LIFETIME = 0.3
SPARK_COUNT = 10
SPARK_SIZE = 3

# Precompute unit circle directions for hexagon vertices
BASE_DIRS = [Vector2(math.cos(math.radians(60*i - 30)),
                     math.sin(math.radians(60*i - 30)))
             for i in range(6)]

def reflect(v, n):
    return v - 2 * v.dot(n) * n

class Spark:
    def __init__(self, pos):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(80, 160)
        self.vel = Vector2(math.cos(angle), math.sin(angle)) * speed
        self.pos = Vector2(pos)
        self.life = SPARK_LIFETIME

    def update(self, dt):
        self.pos += self.vel * dt
        self.life -= dt

    def draw(self, surf):
        alpha = max(0, int(255 * (self.life / SPARK_LIFETIME)))
        s = pygame.Surface((SPARK_SIZE, SPARK_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(s, (*BALL_COLOR, alpha), 
                           (SPARK_SIZE//2, SPARK_SIZE//2), SPARK_SIZE//2)
        surf.blit(s, (self.pos.x - SPARK_SIZE//2, self.pos.y - SPARK_SIZE//2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    angle = 0.0
    sparks = []

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        angle += ROT_SPEED * dt

        for evt in pygame.event.get():
            if evt.type == pygame.QUIT:
                running = False

        # APPLY GRAVITY
        ball_vel.x += GRAVITY.x * dt
        ball_vel.y += GRAVITY.y * dt

        # MOVE BALL
        global ball_pos
        ball_pos += ball_vel * dt

        # COMPUTE ROTATED HEXAGON
        verts = []
        for d in BASE_DIRS:
            # rotate base dir by current angle
            rot = Vector2(
                d.x * math.cos(angle) - d.y * math.sin(angle),
                d.x * math.sin(angle) + d.y * math.cos(angle)
            )
            verts.append(HEX_CENTER + rot * HEX_RADIUS)

        # COMPUTE EDGE NORMALS
        normals = []
        for i in range(6):
            p1 = verts[i]
            p2 = verts[(i+1)%6]
            edge = p2 - p1
            normals.append((p1, p2, Vector2(-edge.y, edge.x).normalize()))

        # COLLISIONS
        for p1, p2, normal in normals:
            to_ball = ball_pos - p1
            dist = to_ball.dot(normal)
            if dist < BALL_RADIUS:
                proj = to_ball.dot((p2-p1).normalize())
                if 0 <= proj <= (p2-p1).length():
                    # reflect and correct penetration
                    ball_vel[:] = reflect(ball_vel, normal)
                    ball_pos += normal * (BALL_RADIUS - dist)
                    # spawn sparks
                    contact = ball_pos - normal * BALL_RADIUS
                    for _ in range(SPARK_COUNT):
                        sparks.append(Spark(contact))
                    break

        # UPDATE & CLEAN UP SPARKS
        for s in sparks[:]:
            s.update(dt)
            if s.life <= 0:
                sparks.remove(s)

        # DRAW
        screen.fill(BG_COLOR)
        # hexagon outline
        pygame.draw.polygon(screen, (180,180,180), verts, width=3)
        # ball shadow & ball
        pygame.draw.circle(screen, BALL_OUTLINE, ball_pos, BALL_RADIUS+2)
        pygame.draw.circle(screen, BALL_COLOR, ball_pos, BALL_RADIUS)
        # sparks
        for s in sparks:
            s.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
