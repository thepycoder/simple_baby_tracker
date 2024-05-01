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
  let foodAmount = "200";
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
    foodAmount = "200";
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
        amount: foodAmount,
        end: endTimestamp,
      }).then(() => {
        lastFoodStart = new Date();
        resetFood();
        updateFoodSinceLast();
      });
    }
  }

  function updateFoodSinceLast() {
    setInterval(() => {
      const now = new Date();
      foodSinceLast = formatTime(now - lastFoodStart);
    }, 1000);
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
  <p class="text-muted text-center mt-2">
    Aan het eten voor: <b class="fs-2">{formatTime(eatDuration)}</b>
  </p>
  <div class="btn-group mt-2 w-100">
    <button
      on:click={() => toggleFoodType("formula")}
      class={foodType === "formula"
        ? "btn btn-primary"
        : "btn btn-outline-primary"}
      ><i class="bi bi-cup-straw"></i> Infant Formula
    </button>
    <button
      on:click={() => toggleFoodType("solid")}
      class={foodType === "solid"
        ? "btn btn-success"
        : "btn btn-outline-success"}
      ><i class="bi bi-apple"></i> Solid Food
    </button>
  </div>
  <div class="input-group mt-2">
    <button
      class="btn btn-outline-secondary"
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
      class="btn btn-outline-secondary"
      type="button"
      on:click={increaseAmount}>+10</button
    >
  </div>
  <button on:click={endFood} class="btn btn-danger w-100 mt-2">Stop eten</button
  >
{:else}
  <p class="text-muted text-center mt-2">
    Tijd sinds laatste maaltijd: <b class="fs-2">{foodSinceLast}</b>
  </p>
  <button
    on:click={startFood}
    class="btn btn-primary w-100 mt-2"
    disabled={isEating}>Start Eten</button
  >
{/if}
