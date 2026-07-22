class PaperBroker:


    def __init__(
        self,
        capital,
        fee
    ):

        self.cash = capital
        self.position = 0

        self.entry = None
        self.stop = None

        self.fee = fee

        self.trades=[]



    def buy(
        self,
        price,
        risk,
        atr,
        time
    ):


        if self.position:
            return


        stop_distance = atr


        risk_money = (
            self.cash *
            risk
        )


        quantity = (
            risk_money /
            stop_distance
        )


        cost = (
            quantity *
            price
        )


        fee = cost*self.fee


        self.cash -= fee


        self.position = quantity

        self.entry = price

        self.stop = (
            price -
            stop_distance
        )


        self.trades.append(
            {
            "entry_time":time,
            "entry":price,
            "qty":quantity,
            "stop":self.stop
            }
        )



    def update(
        self,
        price,
        ma14,
        time
    ):


        if not self.position:
            return



        exit_signal = (

            price < ma14

            or

            price < self.stop

        )


        if exit_signal:


            value = (
                self.position *
                price
            )


            fee=value*self.fee


            pnl = (
                price -
                self.entry
            )*self.position-fee


            self.cash += pnl


            self.trades[-1].update(
                {
                "exit_time":time,
                "exit":price,
                "pnl":pnl
                }
            )


            self.position=0
            self.entry=None