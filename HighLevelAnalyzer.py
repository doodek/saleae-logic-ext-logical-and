# collision_detection_hla.py

# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, ChoicesSetting

class CollisionDetectionHLA(HighLevelAnalyzer):
    # Settings for selecting the two channels to perform collision detection on
    channel1 = ChoicesSetting(
        choices=[],  # This will be populated dynamically by Saleae
        default='Channel 1'
    )
    channel2 = ChoicesSetting(
        choices=[],  # This will be populated dynamically by Saleae
        default='Channel 2'
    )

    # Define the result types
    result_types = {
        'collision': {
            'format': 'Collision detected between {channel1} and {channel2}'
        }
    }

    def __init__(self):
        '''
        Initialize the Collision Detection HLA.
        '''
        # Initialize the state of both channels
        self.channel1_state = False
        self.channel2_state = False
        self.channel1_name = self.channel1
        self.channel2_name = self.channel2
        self.collision_active = False

    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzers and detect collisions.

        Args:
            frame (AnalyzerFrame): The frame from the input analyzer.

        Returns:
            AnalyzerFrame or list of AnalyzerFrame: The collision frame if a collision is detected.
        '''
        # Check which channel the frame is from and update the state
        if frame.channel == self.channel1_name:
            self.channel1_state = frame.data['value']
        elif frame.channel == self.channel2_name:
            self.channel2_state = frame.data['value']
        else:
            # Ignore frames from other channels
            return

        # Check for collision
        if self.channel1_state and self.channel2_state:
            if not self.collision_active:
                # Collision started
                self.collision_start_time = frame.start_time
                self.collision_active = True
        else:
            if self.collision_active:
                # Collision ended
                collision_frame = AnalyzerFrame(
                    'collision',
                    self.collision_start_time,
                    frame.end_time,
                    {
                        'channel1': self.channel1_name,
                        'channel2': self.channel2_name
                    }
                )
                self.collision_active = False
                return collision_frame

    def finish(self):
        '''
        Called when all frames have been processed. If a collision is still active, close it.
        '''
        if self.collision_active:
            collision_frame = AnalyzerFrame(
                'collision',
                self.collision_start_time,
                self.collision_start_time,  # No end time available
                {
                    'channel1': self.channel1_name,
                    'channel2': self.channel2_name
                }
            )
            self.emit(collision_frame)
            self.collision_active = False
