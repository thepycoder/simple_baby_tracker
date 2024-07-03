<script>
  import { formatTime } from "./utils";
  import { db, db_table } from "./firebase";
  import {
    updateDoc,
    doc,
    serverTimestamp,
    collection,
    addDoc,
  } from "firebase/firestore";
  import { foodEntries } from "./stores";

  let isEating = false;
  let foodType = "formula";
  let foodAmount = "240";
  let eatDuration = 0;
  let clockFoodInterval = null;
  let foodStart = null;
  let currentFoodDocId = null;
  let lastFoodStart = null;
  let foodSinceLast = "N/A";

  function resetFood() {
    console.log("isEating to false");
    isEating = false;
    foodType = "formula";
    foodAmount = "240";
    stopFoodClock();
  }

  function startFoodClock() {
    clearInterval(clockFoodInterval);
    clockFoodInterval = setInterval(updateFoodDuration, 1000);
  }

  function updateFoodDuration() {
    if (isEating) {
      const now = new Date();
      const elapsed = now - foodStart;
      eatDuration = Math.floor(elapsed);
    }
  }

  function toggleFoodType(type) {
    foodType = type;
  }

  function startFood() {
    const startTimestamp = serverTimestamp();
    foodStart = new Date();
    isEating = true;
    addDoc(collection(db, db_table), {
      type: "food",
      subtype: foodType,
      start: startTimestamp,
      amount: foodAmount,
    }).then((docRef) => {
      currentFoodDocId = docRef.id;
      startFoodClock();
    });
  }

  function endFood() {
    console.log("endfood");
    const endTimestamp = serverTimestamp();
    if (currentFoodDocId) {
      updateDoc(doc(db, db_table, currentFoodDocId), {
        subtype: foodType,
        amount: foodAmount,
        end: endTimestamp,
      }).then(() => {
        lastFoodStart = new Date();
        resetFood();
        updateFoodSinceLast();
      });
    }
  }

  function updateFoodSinceLastNow() {
    const now = new Date();
    foodSinceLast = formatTime(now - lastFoodStart);
  }

  function updateFoodSinceLast() {
    updateFoodSinceLastNow();
    setInterval(updateFoodSinceLastNow, 1000);
  }

  function stopFoodClock() {
    clearInterval(clockFoodInterval);
  }

  function increaseAmount() {
    foodAmount = (+foodAmount + 10).toString();
  }

  function decreaseAmount() {
    if (+foodAmount > 10) {
      foodAmount = (+foodAmount - 10).toString();
    }
  }

  $: $foodEntries, init();

  function init() {
    const lastFood = $foodEntries[0];

    if (lastFood) {
      isEating = !Boolean(lastFood.end);
      if (lastFood.end) {
        lastFoodStart = lastFood.start;
        updateFoodSinceLast();
      } else {
        currentFoodDocId = lastFood.id;
        foodStart = lastFood.start;
        startFoodClock();
      }
    }
  }
</script>

{#if isEating}
  <div class="card border-danger">
    <div class="row g-0">
      <div class="col-6 d-flex align-items-center">
        <h2 class="card-text text-center display-5 fw-bold m-0 w-100">
          {formatTime(eatDuration)}
        </h2>
      </div>
      <div class="col-6 bg-danger">
        <button on:click={endFood} class="btn btn-danger w-100 h-100"
          ><i class="bi bi-cup-straw" style="font-size: 4em;"></i></button
        >
      </div>
    </div>
  </div>
  <div class="btn-group mt-2 w-100">
    <button
      on:click={() => toggleFoodType("formula")}
      class={foodType === "formula"
        ? "btn w-50 btn-primary"
        : "btn w-50 btn-outline-primary"}
      ><i class="bi bi-cup-straw"></i> Flesje
    </button>
    <button
      on:click={() => toggleFoodType("solid")}
      class={foodType === "solid"
        ? "btn w-50 btn-primary"
        : "btn w-50 btn-outline-primary"}
      ><i class="bi bi-apple"></i> Vaste Voeding
    </button>
  </div>
  <div class="input-group mt-2">
    <button
      class="btn btn-outline-primary"
      type="button"
      on:click={decreaseAmount}>-10</button
    >
    <input
      type="number"
      bind:value={foodAmount}
      class="form-control"
      placeholder="Hoeveel?"
    />
    <button
      class="btn btn-outline-primary"
      type="button"
      on:click={increaseAmount}>+10</button
    >
  </div>
{:else}
  <div class="card border-primary">
    <div class="row g-0">
      <div class="col-6 d-flex align-items-center">
        <h2 class="card-text text-center display-5 fw-bold m-0 w-100">
          {foodSinceLast}
        </h2>
      </div>
      <div class="col-6 bg-primary">
        <button on:click={startFood} class="btn btn-primary w-100 h-100"
          ><i class="bi bi-cup-straw" style="font-size: 4em;"></i></button
        >
      </div>
    </div>
  </div>
{/if}
