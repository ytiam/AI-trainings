- Tried to explore the different step functions for diff environments
    - Blackjack-v1 and CartPole-v1
    - how an action leads to a new observation via step function? Need to understand how in code and function that is implemented

- Understood state vs observation difference

This subtlety confuses almost everyone starting with RL.

---

### 🔹 **State vs Observation**

* **State (`s`)**

  * The *true, complete description* of the environment at a given time.
  * It contains everything needed to predict the **next state** and **reward**, given an action.
  * In theory (MDPs), the agent should know the state to make optimal decisions.

* **Observation (`o`)**

  * What the **agent actually sees**.
  * It may be equal to the state (fully observable) or just a *partial/filtered view* of it (partially observable).
  * This is the input to the agent’s policy/NN.

---

### 🔹 In **CartPole**

* **State** = `[x, x_dot, theta, theta_dot]`

  * `x` → cart position
  * `x_dot` → cart velocity
  * `theta` → pole angle
  * `theta_dot` → pole angular velocity

* **Observation** = same as state (because CartPole is **fully observable**).

So here, `state == observation`.

---

### 🔹 In **Other Environments**

* **Atari (Breakout, Pong, etc.)**

  * State = complete RAM of the game (all variables in memory).
  * Observation = pixels shown on screen.
  * The agent only gets pixels → partial, noisy view.

* **Robotics (real world)**

  * State = all joint positions, velocities, object positions.
  * Observation = camera feed + some sensors (lidar, force sensors).
  * State is not directly accessible; agent only sees observation.

---

### 🔹 Why Important?

* If **observation == state** → it’s a **Markov Decision Process (MDP)**.
* If **observation ≠ state** → it’s a **Partially Observable MDP (POMDP)**.

  * Here, agent might need memory (RNN, LSTM) to infer hidden state.

---

✅ **So in short:**

* **State** = true environment variables.
* **Observation** = what the agent sees (input).
* In CartPole: they are the same. In many real tasks: they are not.

---

- Started with understanding how we can define a custom env in gymnasium
    - But we can postpone this for later learnings