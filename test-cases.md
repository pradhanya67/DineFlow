# DineFlow test cases

| ID | Scenario | Expected outcome |
|---|---|---|
| DF-01 | Place an order at available T01 | Session opens, table becomes occupied, FIFO queue record is created. |
| DF-02 | Start second queued order first | The kitchen rejects it as a FIFO violation. |
| DF-03 | Mark a non-active order ready | The kitchen rejects it. |
| DF-04 | Check only some delivered items | The order remains ready until all items are confirmed. |
| DF-05 | Generate bill for a session with multiple orders | All non-cancelled item lines are combined. |
| DF-06 | Record payment twice | The second attempt is rejected. |
| DF-07 | Confirm checkout before payment | The waiter action is rejected and table remains occupied. |
| DF-08 | Confirm checkout after payment | Bill closes and table returns to available. |
