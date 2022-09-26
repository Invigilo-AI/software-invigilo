import { acceptHMRUpdate, defineStore } from "pinia";
import { ref, computed } from "vue";
import { useStorage } from "@vueuse/core";
import jwt_decode, { JwtPayload } from "jwt-decode";

export type UserData = null | {
  id: number;
  is_superuser: boolean;
  full_name: string;
  email: string;
  company_id: null | number;
  permissions: string[];
};
export type UserAccess = {
  access_token: string;
  user: UserData;
};

export const useUserSession = defineStore("userSession", () => {
  // token will be synced with local storage
  // @see https://vueuse.org/core/usestorage/
  const token = useStorage("token", "");
  const asCompany = useStorage<number | null>("as_company", null);

  const user = ref<Partial<UserData>>();
  const loading = ref(true);

  const isLoggedIn = computed(
    () => token.value !== undefined && token.value !== ""
  );
  const isSuperuser = computed(() => user.value && user.value.is_superuser);

  const viewAsCompany = computed({
    get() {
      return (isSuperuser.value && asCompany.value) || null;
    },
    set(v: number | null) {
      asCompany.value = v;
    },
  });

  function setViewAsCompany(v: number | null) {
    viewAsCompany.value = v;
  }

  function hasPermission(permission: string) {
    return Boolean(
      user.value &&
        user.value.permissions &&
        user.value.permissions.includes(permission)
    );
  }

  function setUser(newUser?: Partial<UserData>) {
    if (token.value) {
      const tokenData = jwt_decode<JwtPayload & { scopes: string[] }>(
        token.value
      );

      if (newUser && tokenData.scopes) {
        newUser.permissions = tokenData.scopes;
      }
    }
    user.value = newUser;
  }

  function setToken(newToken?: string) {
    token.value = newToken;
  }

  function setLoading(newLoading: boolean) {
    loading.value = newLoading;
  }

  async function loginUser(data?: UserAccess | undefined) {
    setToken(data?.access_token);
    setUser(data?.user);
  }

  async function logoutUser() {
    token.value = undefined;
    user.value = undefined;
  }

  return {
    user,
    token,
    isLoggedIn,
    loading,
    loginUser,
    logoutUser,
    setUser,
    setToken,
    setLoading,
    isSuperuser,
    viewAsCompany,
    setViewAsCompany,
    hasPermission
  } as const;
});

/**
 * Pinia supports Hot Module replacement so you can edit your stores and
 * interact with them directly in your app without reloading the page.
 *
 * @see https://pinia.esm.dev/cookbook/hot-module-replacement.html
 * @see https://vitejs.dev/guide/api-hmr.html
 */
if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useUserSession, import.meta.hot));
}
