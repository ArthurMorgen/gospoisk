import { createClient, isSupabaseConfigured } from "@/lib/supabase";

export interface SavedSearch {
  id: string;
  keywords: string[];
  platforms: string[];
  name: string | null;
  created_at: string;
  last_run_at: string | null;
}

export async function getSavedSearches(): Promise<SavedSearch[]> {
  if (!isSupabaseConfigured) return [];
  const supabase = createClient()!;
  const { data, error } = await supabase
    .from("saved_searches")
    .select("*")
    .order("created_at", { ascending: false });
  if (error) {
    console.error("Error fetching saved searches:", error);
    return [];
  }
  return data ?? [];
}

export async function saveSearch(
  keywords: string[],
  platforms: string[],
  name?: string
): Promise<SavedSearch | null> {
  if (!isSupabaseConfigured) return null;
  const supabase = createClient()!;
  const {
    data: { user },
  } = await supabase.auth.getUser();
  if (!user) return null;

  const { data, error } = await supabase
    .from("saved_searches")
    .insert({
      user_id: user.id,
      keywords,
      platforms,
      name: name || keywords.join(", "),
    })
    .select()
    .single();

  if (error) {
    console.error("Error saving search:", error);
    return null;
  }
  return data;
}

export async function deleteSavedSearch(id: string): Promise<boolean> {
  if (!isSupabaseConfigured) return false;
  const supabase = createClient()!;
  const { error } = await supabase.from("saved_searches").delete().eq("id", id);
  if (error) {
    console.error("Error deleting search:", error);
    return false;
  }
  return true;
}

export async function updateLastRun(id: string): Promise<void> {
  if (!isSupabaseConfigured) return;
  const supabase = createClient()!;
  await supabase
    .from("saved_searches")
    .update({ last_run_at: new Date().toISOString() })
    .eq("id", id);
}
