<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useHead } from '@vueuse/head'

import { useDarkmode } from '/@src/stores/darkmode'
import { useUserSession } from '/@src/stores/userSession'
import { useNotyf } from '/@src/composable/useNotyf'
import { useApi } from '/@src/composable/useApi';

export type UserLogin = Record<"username"|"password", string>;

const isLoading = ref(false)
const darkmode = useDarkmode()
const router = useRouter()
const route = useRoute()
const notif = useNotyf()
const api = useApi()
const userSession = useUserSession()
const redirect = route.query.redirect as string

const login = ref({
  username: '',
  password: '',
  // remember: false
})

const errors = ref({
  username: false,
  password: false,
})

const canLogin = computed(() => {
  return login.value.username && login.value.password
})

const handleLogin = async () => {
  if (!isLoading.value) {
    isLoading.value = true


    const { data, error } = await api.post("/login/access-token", new URLSearchParams(login.value)).catch(error => error)

    userSession.loginUser(data)
      
    notif.dismissAll()

    if (data) {
      notif.success(`Welcome back, ${data.user.full_name}`)
      
      if (redirect) {
        router.push(redirect)
      } else {
        router.push({
          name: 'app',
        })
      }
    } else {
      const {detail, fields} = error
      if (fields) {
        errors.value = fields
      } else {
        errors.value = {
          username: false,
          password: false,
        }
        notif.error(detail)
      }
    }

    isLoading.value = false
  }
}

useHead({
  title: 'Auth Login - Invigilo',
})
</script>

<template>
  <div class="auth-wrapper-inner columns is-gapless">
    <!-- Image section (hidden on mobile) -->
    <div class="column login-column is-8 h-hidden-mobile h-hidden-tablet-p hero-banner">
      <div class="hero login-hero is-fullheight is-app-grey">
        <div class="hero-body">
          <div class="container">
            <div class="columns">
              <div class="column">
                <img
                  class="hero-image"
                  src="/@src/assets/illustrations/apps/station.svg"
                  alt=""
                />
              </div>
            </div>
          </div>
        </div>
        <div class="hero-footer">
          <p class="has-text-centered"></p>
        </div>
      </div>
    </div>

    <!-- Form section -->
    <div class="column is-4">
      <div class="hero is-fullheight is-white">
        <div class="hero-heading">
          <label
            class="dark-mode ml-auto"
            tabindex="0"
            @keydown.space.prevent="(e) => e.target.click()"
          >
            <input
              type="checkbox"
              :checked="!darkmode.isDark"
              @change="darkmode.onChange"
            />
            <span></span>
          </label>
          <div class="auth-logo">
            <RouterLink :to="{ name: 'index' }">
              <AnimatedLogo width="36px" height="36px" />
            </RouterLink>
          </div>
        </div>
        <div class="hero-body">
          <div class="container">
            <div class="columns">
              <div class="column is-12">
                <div class="auth-content">
                  <h2>Welcome Back.</h2>
                  <p>Please sign in to your account</p>
                  <!-- <RouterLink :to="{ name: 'auth-signup' }">
                    I do not have an account yet
                  </RouterLink> -->
                </div>
                <div class="auth-form-wrapper">
                  <!-- Login Form -->
                  <form @submit.prevent="handleLogin">
                    <div class="login-form">
                      <!-- Username -->
                      <VField>
                        <VControl icon="feather:user" :has-error="errors.username">
                          <input
                            v-model="login.username"
                            class="input"
                            type="text"
                            placeholder="Username"
                            autocomplete="username"
                          />
                          <p v-if="errors.username" class="help text-danger">{{ errors.username }}</p>
                        </VControl>
                      </VField>

                      <!-- Password -->
                      <VField>
                        <VControl icon="feather:lock" :has-error="errors.password">
                          <input
                            v-model="login.password"
                            class="input"
                            type="password"
                            placeholder="Password"
                            autocomplete="current-password"
                          />
                          <p v-if="errors.password" class="help text-danger">{{ errors.password }}</p>
                        </VControl>
                      </VField>

                      <!-- Switch -->
                      <!-- <VControl class="setting-item">
                        <label for="remember-me" class="remember-toggle form-switch is-primary">
                          <input id="remember-me" type="checkbox" class="is-switch" v-model="login.remember" />
                          <span class="toggler">
                            <span class="active">
                              <i aria-hidden="true" class="iconify" data-icon="feather:check"></i>
                            </span>
                            <span class="inactive">
                              <i
                                aria-hidden="true"
                                class="iconify"
                                data-icon="feather:circle"
                              ></i>
                            </span>
                          </span>
                        </label>
                        <div class="setting-meta">
                          <label for="remember-me">
                            <span>Remember Me</span>
                          </label>
                        </div>
                      </VControl> -->

                      <!-- Submit -->
                      <VControl class="login">
                        <VButton
                          :loading="isLoading"
                          color="primary"
                          type="submit"
                          bold
                          fullwidth
                          raised
                          :disabled="!canLogin"
                        >
                          Sign In
                        </VButton>
                      </VControl>

                      <div class="forgot-link has-text-centered">
                        <a>Forgot Password?</a>
                      </div>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import '../../scss/abstracts/mixins';

.hero-image {
  position: relative;
  z-index: 2;
  display: block;
  margin: auto;
  max-width: 60%;
  width: 60%;
  max-height: 100%;
}

.remember-toggle {
  width: 65px;
  display: block;
  position: relative;
  cursor: pointer;
  font-size: 22px;
  user-select: none;
  transform: scale(0.9);

  input {
    position: absolute;
    opacity: 0;
    cursor: pointer;

    &:checked ~ .toggler {
      border-color: var(--primary);

      .active,
      .inactive {
        transform: translateX(100%) rotate(360deg);
      }

      .active {
        opacity: 1;
      }

      .inactive {
        opacity: 0;
      }
    }
  }

  .toggler {
    position: relative;
    display: block;
    height: 34px;
    width: 61px;
    border: 2px solid var(--placeholder);
    border-radius: 100px;
    transition: all 0.3s; // transition-all test

    .active,
    .inactive {
      position: absolute;
      top: 2px;
      left: 2px;
      height: 26px;
      width: 26px;
      border-radius: var(--radius-rounded);
      background: black;
      display: flex;
      justify-content: center;
      align-items: center;
      transform: translateX(0) rotate(0);
      transition: all 0.3s ease;

      svg {
        color: var(--white);
        height: 14px;
        width: 14px;
        stroke-width: 3px;
      }
    }

    .inactive {
      background: var(--placeholder);
      border-color: var(--placeholder);
      opacity: 1;
      z-index: 1;
    }

    .active {
      background: var(--primary);
      border-color: var(--primary);
      opacity: 0;
      z-index: 0;
    }
  }
}
</style>