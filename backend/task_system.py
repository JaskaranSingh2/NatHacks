"""
Complete Task System for AssistiveCoach
Real ADL tasks with step-by-step guidance, ArUco markers, and TTS
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time

class TaskState(Enum):
    IDLE = "idle"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    STEP_COMPLETE = "step_complete"
    TASK_COMPLETE = "task_complete"
    PAUSED = "paused"

@dataclass
class TaskStep:
    """Individual step in a task"""
    step_num: int
    title: str
    instruction: str
    hint: str
    duration_s: int
    aruco_marker_id: Optional[int] = None  # ArUco marker to look for
    requires_hand_motion: bool = False     # Whether hand tracking is needed
    voice_prompt: Optional[str] = None     # TTS message
    
@dataclass
class Task:
    """Complete ADL task definition"""
    task_id: str
    name: str
    category: str
    description: str
    icon: str
    steps: List[TaskStep]
    total_time_estimate_s: int
    difficulty: str = "easy"  # easy, medium, hard
    
    def get_step(self, step_num: int) -> Optional[TaskStep]:
        """Get a specific step"""
        for step in self.steps:
            if step.step_num == step_num:
                return step
        return None

# ============================================================================
# TASK DEFINITIONS
# ============================================================================

TASKS = {
    "brush_teeth": Task(
        task_id="brush_teeth",
        name="Brush Teeth",
        category="oral_care",
        description="Complete tooth brushing routine",
        icon="🪥",
        total_time_estimate_s=120,
        difficulty="easy",
        steps=[
            TaskStep(
                step_num=1,
                title="Prepare Toothbrush",
                instruction="Wet toothbrush and apply toothpaste",
                hint="Hold marker ID 1 near sink",
                duration_s=15,
                aruco_marker_id=1,
                voice_prompt="Step 1: Wet your toothbrush and apply a pea-sized amount of toothpaste"
            ),
            TaskStep(
                step_num=2,
                title="Brush Upper Teeth",
                instruction="Brush top teeth in small circles",
                hint="Gentle pressure, circular motions",
                duration_s=30,
                aruco_marker_id=2,
                requires_hand_motion=True,
                voice_prompt="Step 2: Brush your upper teeth using gentle circular motions"
            ),
            TaskStep(
                step_num=3,
                title="Brush Lower Teeth",
                instruction="Brush bottom teeth in small circles",
                hint="Don't forget the molars",
                duration_s=30,
                aruco_marker_id=3,
                requires_hand_motion=True,
                voice_prompt="Step 3: Now brush your lower teeth, including the back molars"
            ),
            TaskStep(
                step_num=4,
                title="Brush Tongue",
                instruction="Gently brush your tongue",
                hint="Front to back, removes bacteria",
                duration_s=15,
                aruco_marker_id=4,
                voice_prompt="Step 4: Gently brush your tongue from back to front"
            ),
            TaskStep(
                step_num=5,
                title="Rinse",
                instruction="Rinse mouth thoroughly with water",
                hint="Swish and spit",
                duration_s=15,
                aruco_marker_id=1,
                voice_prompt="Step 5: Rinse your mouth thoroughly with water"
            ),
            TaskStep(
                step_num=6,
                title="Clean Up",
                instruction="Rinse toothbrush and put away",
                hint="Store upright to air dry",
                duration_s=15,
                aruco_marker_id=1,
                voice_prompt="Final step: Rinse your toothbrush and store it upright. Great job!"
            ),
        ]
    ),
    
    "wash_face": Task(
        task_id="wash_face",
        name="Wash Face",
        category="hygiene",
        description="Complete face washing routine",
        icon="🧼",
        total_time_estimate_s=90,
        difficulty="easy",
        steps=[
            TaskStep(
                step_num=1,
                title="Wet Face",
                instruction="Splash face with lukewarm water",
                hint="Not too hot or cold",
                duration_s=10,
                aruco_marker_id=1,
                voice_prompt="Step 1: Splash your face with lukewarm water"
            ),
            TaskStep(
                step_num=2,
                title="Apply Cleanser",
                instruction="Apply face wash to hands",
                hint="Use a dime-sized amount",
                duration_s=10,
                aruco_marker_id=2,
                voice_prompt="Step 2: Apply a dime-sized amount of cleanser to your hands"
            ),
            TaskStep(
                step_num=3,
                title="Massage Face",
                instruction="Gently massage cleanser in circles",
                hint="Avoid eye area",
                duration_s=30,
                aruco_marker_id=3,
                requires_hand_motion=True,
                voice_prompt="Step 3: Gently massage the cleanser onto your face in circular motions"
            ),
            TaskStep(
                step_num=4,
                title="Rinse Thoroughly",
                instruction="Rinse all cleanser from face",
                hint="Make sure no soap remains",
                duration_s=20,
                aruco_marker_id=1,
                voice_prompt="Step 4: Rinse thoroughly until all cleanser is removed"
            ),
            TaskStep(
                step_num=5,
                title="Pat Dry",
                instruction="Pat face dry with clean towel",
                hint="Don't rub, gentle pats",
                duration_s=10,
                aruco_marker_id=4,
                voice_prompt="Step 5: Gently pat your face dry with a clean towel. Well done!"
            ),
        ]
    ),
    
    "comb_hair": Task(
        task_id="comb_hair",
        name="Comb Hair",
        category="grooming",
        description="Brush and style hair",
        icon="💇",
        total_time_estimate_s=60,
        difficulty="easy",
        steps=[
            TaskStep(
                step_num=1,
                title="Section Hair",
                instruction="Divide hair into manageable sections",
                hint="Start with one side",
                duration_s=10,
                aruco_marker_id=1,
                voice_prompt="Step 1: Divide your hair into sections to make brushing easier"
            ),
            TaskStep(
                step_num=2,
                title="Detangle Ends",
                instruction="Gently comb through the ends first",
                hint="Work out knots slowly",
                duration_s=20,
                aruco_marker_id=2,
                requires_hand_motion=True,
                voice_prompt="Step 2: Start at the ends and gently work out any tangles"
            ),
            TaskStep(
                step_num=3,
                title="Brush from Roots",
                instruction="Brush from roots to ends",
                hint="Smooth, even strokes",
                duration_s=20,
                aruco_marker_id=3,
                requires_hand_motion=True,
                voice_prompt="Step 3: Now brush from roots to ends with smooth strokes"
            ),
            TaskStep(
                step_num=4,
                title="Style",
                instruction="Style hair as desired",
                hint="Use your preferred style",
                duration_s=10,
                aruco_marker_id=4,
                voice_prompt="Step 4: Style your hair however you like. You look great!"
            ),
        ]
    ),
    
    "draw_eyebrows": Task(
        task_id="draw_eyebrows",
        name="Draw Eyebrows",
        category="grooming",
        description="Apply eyebrow makeup with pencil or powder",
        icon="�",
        total_time_estimate_s=120,
        difficulty="medium",
        steps=[
            TaskStep(
                step_num=1,
                title="Prepare Tools",
                instruction="Get eyebrow pencil/powder and brush ready",
                hint="Have all your tools within reach",
                duration_s=10,
                aruco_marker_id=1,
                voice_prompt="Step 1: Get your eyebrow pencil, powder, and brush ready"
            ),
            TaskStep(
                step_num=2,
                title="Brush Brows",
                instruction="Brush eyebrows upward with spoolie",
                hint="This reveals your natural shape",
                duration_s=15,
                aruco_marker_id=2,
                requires_hand_motion=True,
                voice_prompt="Step 2: Brush your eyebrows upward with a spoolie to see the natural shape"
            ),
            TaskStep(
                step_num=3,
                title="Fill Sparse Areas",
                instruction="Use light strokes to fill sparse areas",
                hint="Start from the inner brow",
                duration_s=30,
                aruco_marker_id=3,
                requires_hand_motion=True,
                voice_prompt="Step 3: Use light strokes to fill in any sparse areas, starting from the inner brow"
            ),
            TaskStep(
                step_num=4,
                title="Define Shape",
                instruction="Define the arch and tail of the brow",
                hint="Follow your natural brow shape",
                duration_s=30,
                aruco_marker_id=4,
                requires_hand_motion=True,
                voice_prompt="Step 4: Define the arch and tail, following your natural brow shape"
            ),
            TaskStep(
                step_num=5,
                title="Blend and Set",
                instruction="Blend with spoolie and apply brow gel",
                hint="This keeps everything in place",
                duration_s=20,
                requires_hand_motion=True,
                voice_prompt="Step 5: Blend everything with a spoolie and apply brow gel to set"
            ),
            TaskStep(
                step_num=6,
                title="Final Check",
                instruction="Check symmetry and make any final adjustments",
                hint="Step back and look at both brows together",
                duration_s=15,
                voice_prompt="Step 6: Check that both brows are symmetrical. Perfect! You look amazing!"
            ),
        ]
    ),
}

@dataclass
class TaskSession:
    """Active task session state"""
    task: Task
    state: TaskState = TaskState.READY
    current_step: int = 1
    step_start_time: Optional[float] = None
    total_start_time: Optional[float] = None
    last_marker_seen: Optional[int] = None
    hand_motion_detected: bool = False
    
    def start(self):
        """Start the task"""
        self.state = TaskState.IN_PROGRESS
        self.current_step = 1
        self.total_start_time = time.time()
        self.step_start_time = time.time()
        
    def get_current_step(self) -> Optional[TaskStep]:
        """Get current step details"""
        return self.task.get_step(self.current_step)
    
    def get_time_left_in_step(self) -> int:
        """Get seconds remaining in current step"""
        if not self.step_start_time:
            return 0
        step = self.get_current_step()
        if not step:
            return 0
        elapsed = time.time() - self.step_start_time
        remaining = max(0, step.duration_s - int(elapsed))
        return remaining
    
    def advance_step(self):
        """Move to next step"""
        if self.current_step >= len(self.task.steps):
            self.state = TaskState.TASK_COMPLETE
            return False
        
        self.current_step += 1
        self.step_start_time = time.time()
        self.hand_motion_detected = False
        
        if self.current_step > len(self.task.steps):
            self.state = TaskState.TASK_COMPLETE
            return False
        
        return True
    
    def check_step_complete(self) -> bool:
        """Check if current step conditions are met"""
        step = self.get_current_step()
        if not step:
            return False
        
        # Time requirement
        time_left = self.get_time_left_in_step()
        if time_left > 0:
            return False
        
        # ArUco marker requirement
        if step.aruco_marker_id and self.last_marker_seen != step.aruco_marker_id:
            return False
        
        # Hand motion requirement
        if step.requires_hand_motion and not self.hand_motion_detected:
            return False
        
        return True
    
    def to_overlay_message(self) -> Dict[str, Any]:
        """Convert to overlay message for frontend"""
        step = self.get_current_step()
        if not step:
            return {}
        
        time_left = self.get_time_left_in_step()
        progress = self.current_step / len(self.task.steps)
        
        return {
            "type": "overlay.set",
            "hud": {
                "title": self.task.name,
                "step": f"Step {self.current_step} of {len(self.task.steps)}",
                "subtitle": step.title,
                "instruction": step.instruction,
                "hint": step.hint,
                "time_left_s": time_left,
                "max_time_s": step.duration_s,
                "progress": progress
            },
            "shapes": []  # Will be populated with ArUco/hand overlays
        }

def get_all_tasks() -> List[Dict[str, Any]]:
    """Get list of all available tasks for menu"""
    return [
        {
            "task_id": task.task_id,
            "name": task.name,
            "icon": task.icon,
            "category": task.category,
            "description": task.description,
            "duration_s": task.total_time_estimate_s,
            "difficulty": task.difficulty,
            "num_steps": len(task.steps)
        }
        for task in TASKS.values()
    ]

def start_task(task_id: str) -> Optional[TaskSession]:
    """Start a new task session"""
    task = TASKS.get(task_id)
    if not task:
        return None
    
    session = TaskSession(task=task)
    session.start()
    return session
