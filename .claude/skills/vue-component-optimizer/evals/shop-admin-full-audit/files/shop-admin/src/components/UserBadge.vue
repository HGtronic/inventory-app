<script setup>
defineProps({
  user: { type: Object, required: true },
});
</script>

<template>
  <div class="user-badge">
    <span class="avatar">{{ user.avatarInitials }}</span>
    <div class="user-text">
      <span class="user-name">{{ user.name }}</span>
      <span class="user-role">{{ user.role }}</span>
    </div>
  </div>
</template>

<style scoped>
.user-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-top: 1px solid #e2e8f0;
}

.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  background: #475569;
  border-radius: 50%;
}

.user-text {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.user-name {
  font-weight: 600;
}

.user-role {
  font-size: 12px;
  color: #64748b;
}
</style>
