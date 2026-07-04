class SupervisorAgent:


    def decide(self, state):

        if state.get("status") == "WAITING_FOR_REVIEW":

            return "END"


        return "CONTINUE"