<!-- ConfirmModal.svelte -->
<script>
  import { createEventDispatcher } from "svelte";

  export let message = "";
  export let show = false;

  const dispatch = createEventDispatcher();

  function confirm() {
    dispatch("confirm");
  }

  function cancel() {
    dispatch("cancel");
  }
</script>

{#if show}
  <div class="modal show" tabindex="-1" style="display: block;">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Confirmation</h5>
        </div>
        <div class="modal-body">
          <p>{message}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={cancel}>Cancel</button>
          <button class="btn btn-primary" on:click={confirm}>Confirm</button>
        </div>
      </div>
    </div>
    <div class="modal show"></div>
  </div>
{/if}

<!-- <style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    z-index: 1040;
    width: 100vw;
    height: 100vh;
    background-color: #000;
    opacity: 0.5;
  }
  .modal {
    position: fixed;
    top: 50%;
    left: 50%;
    z-index: 1050;
    display: none;
    width: 100%;
    max-width: 500px;
    transform: translate(-50%, -50%);
  }
</style> -->
