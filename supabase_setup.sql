-- 1. Enable required extensions
create extension if not exists postgis;
create extension if not exists "pgcrypto";

-------------------------------------------------------------------
-- 2. intersections
-------------------------------------------------------------------
create table if not exists public.intersections (
  id          uuid                  primary key default gen_random_uuid(),
  name        varchar(255)          not null,
  location    geography(Point,4326) not null,
  created_at  timestamptz           not null default now()
);

create index if not exists intersections_location_gix
  on public.intersections
  using gist (location);

comment on table public.intersections is 'Street‐intersection points';
comment on column public.intersections.id         is 'Unique identifier for the intersection';
comment on column public.intersections.name       is 'Intersection name, e.g., "Main St & 5th Ave"';
comment on column public.intersections.location   is 'Geographic location (lat/long)';
comment on column public.intersections.created_at is 'Timestamp of record creation';

-------------------------------------------------------------------
-- 3. traffic_data
-------------------------------------------------------------------
create table if not exists public.traffic_data (
  id               uuid             primary key default gen_random_uuid(),
  intersection_id  uuid             not null references public.intersections(id),
  traffic_density  double precision not null,
  light_timings    jsonb            not null,
  "timestamp"      timestamptz      not null default now()
);

create index if not exists traffic_data_intersection_id_idx
  on public.traffic_data(intersection_id);

comment on table public.traffic_data is 'Traffic & light‑timing records for each intersection';
comment on column public.traffic_data.id              is 'Unique identifier for the record';
comment on column public.traffic_data.intersection_id is 'References intersections(id)';
comment on column public.traffic_data.traffic_density is 'Traffic density value';
comment on column public.traffic_data.light_timings   is 'Current light timings (green, red)';
comment on column public.traffic_data."timestamp"     is 'Time of data recording';

-------------------------------------------------------------------
-- 4. optimized_timings
-------------------------------------------------------------------
create table if not exists public.optimized_timings (
  id                uuid             primary key default gen_random_uuid(),
  traffic_data_id   uuid             not null references public.traffic_data(id),
  optimized_timings jsonb            not null,
  "timestamp"       timestamptz      not null default now()
);

create index if not exists optimized_timings_data_id_idx
  on public.optimized_timings(traffic_data_id);

comment on table public.optimized_timings is 'Optimized signal‑timing records per traffic_data entry';
comment on column public.optimized_timings.id                is 'Unique identifier for the record';
comment on column public.optimized_timings.traffic_data_id   is 'References traffic_data(id)';
comment on column public.optimized_timings.optimized_timings is 'Optimized timings (green, red)';
comment on column public.optimized_timings."timestamp"       is 'Time of optimization';

-------------------------------------------------------------------
-- 5. logs
-------------------------------------------------------------------
create table if not exists public.logs (
  id               uuid        primary key default gen_random_uuid(),
  traffic_data_id  uuid        not null references public.traffic_data(id),
  log_message      text,
  created_at       timestamptz not null default now()
);

create index if not exists logs_traffic_data_id_idx
  on public.logs(traffic_data_id);

comment on table public.logs is 'Log or chat messages associated with traffic_data entries';
comment on column public.logs.id              is 'Unique identifier for the record';
comment on column public.logs.traffic_data_id is 'References traffic_data(id)';
comment on column public.logs.log_message     is 'Log or chat message';
comment on column public.logs.created_at      is 'Time of logging';
