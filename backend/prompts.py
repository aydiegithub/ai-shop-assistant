from dataclasses import dataclass

delimiter = "####"

example_user_dict = {'GPU intensity': "high",
                    'Display quality':"high",
                    'Portability': "low",
                    'Multitasking': "high",
                    'Processing speed': "high",
                    'Budget': "150000"}

example_user_req = {'GPU intensity': "_",
                    'Display quality': "_",
                    'Portability': "_",
                    'Multitasking': "_",
                    'Processing speed': "_",
                    'Budget': "_"}

@dataclass
class SystemInstruction:
    system_instruction: str = """ 

    """