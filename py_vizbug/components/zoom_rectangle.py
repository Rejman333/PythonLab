class ZoomRectangle:
    def __init__(self):
        self.start_position = None
        self.end_position = None
        self.is_rectangle_finished = False
        self.rectangle_id = None

    def create(self, canvas, start_position):
        self.start_position = start_position
        self.end_position = None
        self.is_rectangle_finished = False
        self.rectangle_id = None

        self.rectangle_id = canvas.create_rectangle(
            self.start_position[0], self.start_position[1], self.start_position[0], self.start_position[1],
            outline="red", width=1
        )

    def move(self, canvas, end_position):
        self.end_position = end_position
        canvas.coords(
            self.rectangle_id,
            self.start_position[0],
            self.start_position[1],
            self.end_position[0],
            self.end_position[1]
        )

    def finish(self):
        new_start = (min(self.start_position[0], self.end_position[0]),
                     min(self.start_position[1], self.end_position[1]))
        new_end = (max(self.start_position[0], self.end_position[0]),
                   max(self.start_position[1], self.end_position[1]))
        self.start_position = new_start
        self.end_position = new_end
        self.is_rectangle_finished = True

    def is_clicked(self, mouse_position):
        x, y = mouse_position
        return (self.start_position[0] <= x <= self.end_position[0] and
                self.start_position[1] <= y <= self.end_position[1])

    def destroy(self, canvas):
        for item in canvas.find_all():
            if canvas.type(item) == "rectangle":
                canvas.delete(item)
        self.rectangle_id = None
        self.start_position = None
        self.end_position = None
        self.is_rectangle_finished = False
