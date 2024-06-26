PGDMP     ,    :    	            |           vault    15.5    15.2 ?    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    16511    vault    DATABASE     p   CREATE DATABASE vault WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF8';
    DROP DATABASE vault;
                cloudsqlsuperuser    false            �           0    0    SCHEMA public    ACL     1   GRANT ALL ON SCHEMA public TO cloudsqlsuperuser;
                   pg_database_owner    false    6                        3079    16561    pgcrypto 	   EXTENSION     <   CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
    DROP EXTENSION pgcrypto;
                   false            �           0    0    EXTENSION pgcrypto    COMMENT     <   COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';
                        false    2            �           0    0 4   FUNCTION pg_replication_origin_advance(text, pg_lsn)    ACL     c   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_advance(text, pg_lsn) TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    268            �           0    0 +   FUNCTION pg_replication_origin_create(text)    ACL     Z   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_create(text) TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    272            �           0    0 )   FUNCTION pg_replication_origin_drop(text)    ACL     X   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_drop(text) TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    263            �           0    0 (   FUNCTION pg_replication_origin_oid(text)    ACL     W   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_oid(text) TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    273            �           0    0 6   FUNCTION pg_replication_origin_progress(text, boolean)    ACL     e   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_progress(text, boolean) TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    269            �           0    0 1   FUNCTION pg_replication_origin_session_is_setup()    ACL     `   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_session_is_setup() TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    264            �           0    0 8   FUNCTION pg_replication_origin_session_progress(boolean)    ACL     g   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_session_progress(boolean) TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    265            �           0    0 .   FUNCTION pg_replication_origin_session_reset()    ACL     ]   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_session_reset() TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    266            �           0    0 2   FUNCTION pg_replication_origin_session_setup(text)    ACL     a   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_session_setup(text) TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    267            �           0    0 +   FUNCTION pg_replication_origin_xact_reset()    ACL     Z   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_xact_reset() TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    270            �           0    0 K   FUNCTION pg_replication_origin_xact_setup(pg_lsn, timestamp with time zone)    ACL     z   GRANT ALL ON FUNCTION pg_catalog.pg_replication_origin_xact_setup(pg_lsn, timestamp with time zone) TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    225            �           0    0    FUNCTION pg_show_replication_origin_status(OUT local_id oid, OUT external_id text, OUT remote_lsn pg_lsn, OUT local_lsn pg_lsn)    ACL     �   GRANT ALL ON FUNCTION pg_catalog.pg_show_replication_origin_status(OUT local_id oid, OUT external_id text, OUT remote_lsn pg_lsn, OUT local_lsn pg_lsn) TO cloudsqlsuperuser;
       
   pg_catalog          cloudsqladmin    false    271                       1255    16609    log_replication_changes()    FUNCTION     k  CREATE FUNCTION public.log_replication_changes() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ 
BEGIN 
    IF TG_OP = 'INSERT' THEN 
        INSERT INTO replication_logs (table_name, operation, data) 
        VALUES (TG_TABLE_NAME, 'INSERT', to_jsonb(NEW)); 
    ELSIF TG_OP = 'UPDATE' THEN 
        INSERT INTO replication_logs (table_name, operation, data) 
        VALUES (TG_TABLE_NAME, 'UPDATE', to_jsonb(NEW)); 
    ELSIF TG_OP = 'DELETE' THEN 
        INSERT INTO replication_logs (table_name, operation, data) 
        VALUES (TG_TABLE_NAME, 'DELETE', to_jsonb(OLD)); 
    END IF; 
    RETURN NULL; 
END; 
$$;
 0   DROP FUNCTION public.log_replication_changes();
       public          postgres    false            �            1259    16599    replication_logs    TABLE     %  CREATE TABLE public.replication_logs (
    id integer NOT NULL,
    table_name text,
    operation character varying(10),
    data jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    processed boolean DEFAULT false,
    processed_at timestamp without time zone
);
 $   DROP TABLE public.replication_logs;
       public         heap    postgres    false            �            1259    16598    replication_logs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.replication_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.replication_logs_id_seq;
       public          postgres    false    224            �           0    0    replication_logs_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.replication_logs_id_seq OWNED BY public.replication_logs.id;
          public          postgres    false    223            �            1259    16522    user_credentials    TABLE     �   CREATE TABLE public.user_credentials (
    id integer NOT NULL,
    user_id integer NOT NULL,
    hashed_password character varying(32) NOT NULL
);
 $   DROP TABLE public.user_credentials;
       public         heap    postgres    false            �            1259    16521    user_credentials_id_seq    SEQUENCE     �   CREATE SEQUENCE public.user_credentials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.user_credentials_id_seq;
       public          postgres    false    218            �           0    0    user_credentials_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.user_credentials_id_seq OWNED BY public.user_credentials.id;
          public          postgres    false    217            �            1259    16534    user_masterkey    TABLE     �   CREATE TABLE public.user_masterkey (
    id integer NOT NULL,
    user_id integer NOT NULL,
    encryption_key text NOT NULL,
    encrypted_masterkey text NOT NULL
);
 "   DROP TABLE public.user_masterkey;
       public         heap    postgres    false            �            1259    16533    user_masterkey_id_seq    SEQUENCE     �   CREATE SEQUENCE public.user_masterkey_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.user_masterkey_id_seq;
       public          postgres    false    220            �           0    0    user_masterkey_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.user_masterkey_id_seq OWNED BY public.user_masterkey.id;
          public          postgres    false    219            �            1259    16513    users    TABLE     '  CREATE TABLE public.users (
    id integer NOT NULL,
    firstname character varying(50) NOT NULL,
    lastname character varying(50) NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(255) NOT NULL,
    creation_timestamp timestamp without time zone NOT NULL
);
    DROP TABLE public.users;
       public         heap    postgres    false            �            1259    16512    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public          postgres    false    216            �           0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public          postgres    false    215            �            1259    16548    vault    TABLE     �   CREATE TABLE public.vault (
    id integer NOT NULL,
    user_id integer NOT NULL,
    vault_account_name character varying(50) NOT NULL,
    vault_user_name character varying(50) NOT NULL,
    vault_encrypted_passwords text NOT NULL
);
    DROP TABLE public.vault;
       public         heap    postgres    false            �            1259    16547    vault_id_seq    SEQUENCE     �   CREATE SEQUENCE public.vault_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.vault_id_seq;
       public          postgres    false    222            �           0    0    vault_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.vault_id_seq OWNED BY public.vault.id;
          public          postgres    false    221            
           2604    16602    replication_logs id    DEFAULT     z   ALTER TABLE ONLY public.replication_logs ALTER COLUMN id SET DEFAULT nextval('public.replication_logs_id_seq'::regclass);
 B   ALTER TABLE public.replication_logs ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    224    223    224                       2604    16525    user_credentials id    DEFAULT     z   ALTER TABLE ONLY public.user_credentials ALTER COLUMN id SET DEFAULT nextval('public.user_credentials_id_seq'::regclass);
 B   ALTER TABLE public.user_credentials ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    218    217    218                       2604    16537    user_masterkey id    DEFAULT     v   ALTER TABLE ONLY public.user_masterkey ALTER COLUMN id SET DEFAULT nextval('public.user_masterkey_id_seq'::regclass);
 @   ALTER TABLE public.user_masterkey ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    220    219    220                       2604    16516    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    216    215    216            	           2604    16551    vault id    DEFAULT     d   ALTER TABLE ONLY public.vault ALTER COLUMN id SET DEFAULT nextval('public.vault_id_seq'::regclass);
 7   ALTER TABLE public.vault ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    221    222    222            �          0    16599    replication_logs 
   TABLE DATA           p   COPY public.replication_logs (id, table_name, operation, data, created_at, processed, processed_at) FROM stdin;
    public          postgres    false    224   kJ       �          0    16522    user_credentials 
   TABLE DATA           H   COPY public.user_credentials (id, user_id, hashed_password) FROM stdin;
    public          postgres    false    218   �J       �          0    16534    user_masterkey 
   TABLE DATA           Z   COPY public.user_masterkey (id, user_id, encryption_key, encrypted_masterkey) FROM stdin;
    public          postgres    false    220   �J       �          0    16513    users 
   TABLE DATA           ]   COPY public.users (id, firstname, lastname, username, email, creation_timestamp) FROM stdin;
    public          postgres    false    216   �J       �          0    16548    vault 
   TABLE DATA           l   COPY public.vault (id, user_id, vault_account_name, vault_user_name, vault_encrypted_passwords) FROM stdin;
    public          postgres    false    222   �J       �           0    0    replication_logs_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.replication_logs_id_seq', 1, false);
          public          postgres    false    223            �           0    0    user_credentials_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.user_credentials_id_seq', 1, false);
          public          postgres    false    217            �           0    0    user_masterkey_id_seq    SEQUENCE SET     D   SELECT pg_catalog.setval('public.user_masterkey_id_seq', 1, false);
          public          postgres    false    219            �           0    0    users_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.users_id_seq', 1, false);
          public          postgres    false    215            �           0    0    vault_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.vault_id_seq', 1, false);
          public          postgres    false    221                       2606    16608 &   replication_logs replication_logs_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.replication_logs
    ADD CONSTRAINT replication_logs_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.replication_logs DROP CONSTRAINT replication_logs_pkey;
       public            postgres    false    224                       2606    16527 &   user_credentials user_credentials_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.user_credentials
    ADD CONSTRAINT user_credentials_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.user_credentials DROP CONSTRAINT user_credentials_pkey;
       public            postgres    false    218                       2606    16541 "   user_masterkey user_masterkey_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.user_masterkey
    ADD CONSTRAINT user_masterkey_pkey PRIMARY KEY (id);
 L   ALTER TABLE ONLY public.user_masterkey DROP CONSTRAINT user_masterkey_pkey;
       public            postgres    false    220                       2606    16518    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    216                       2606    16520    users users_username_key 
   CONSTRAINT     W   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);
 B   ALTER TABLE ONLY public.users DROP CONSTRAINT users_username_key;
       public            postgres    false    216                       2606    16555    vault vault_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.vault
    ADD CONSTRAINT vault_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.vault DROP CONSTRAINT vault_pkey;
       public            postgres    false    222                       2620    16611 $   user_credentials replication_changes    TRIGGER     �   CREATE TRIGGER replication_changes AFTER INSERT OR DELETE OR UPDATE ON public.user_credentials FOR EACH ROW EXECUTE FUNCTION public.log_replication_changes();
 =   DROP TRIGGER replication_changes ON public.user_credentials;
       public          postgres    false    262    218                       2620    16612 "   user_masterkey replication_changes    TRIGGER     �   CREATE TRIGGER replication_changes AFTER INSERT OR DELETE OR UPDATE ON public.user_masterkey FOR EACH ROW EXECUTE FUNCTION public.log_replication_changes();
 ;   DROP TRIGGER replication_changes ON public.user_masterkey;
       public          postgres    false    262    220                       2620    16610    users replication_changes    TRIGGER     �   CREATE TRIGGER replication_changes AFTER INSERT OR DELETE OR UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.log_replication_changes();
 2   DROP TRIGGER replication_changes ON public.users;
       public          postgres    false    262    216                       2620    16613    vault replication_changes    TRIGGER     �   CREATE TRIGGER replication_changes AFTER INSERT OR DELETE OR UPDATE ON public.vault FOR EACH ROW EXECUTE FUNCTION public.log_replication_changes();
 2   DROP TRIGGER replication_changes ON public.vault;
       public          postgres    false    222    262                       2606    16528 .   user_credentials user_credentials_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_credentials
    ADD CONSTRAINT user_credentials_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
 X   ALTER TABLE ONLY public.user_credentials DROP CONSTRAINT user_credentials_user_id_fkey;
       public          postgres    false    218    3854    216                       2606    16542 *   user_masterkey user_masterkey_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_masterkey
    ADD CONSTRAINT user_masterkey_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
 T   ALTER TABLE ONLY public.user_masterkey DROP CONSTRAINT user_masterkey_user_id_fkey;
       public          postgres    false    216    3854    220                       2606    16556    vault vault_user_id_fkey    FK CONSTRAINT     w   ALTER TABLE ONLY public.vault
    ADD CONSTRAINT vault_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);
 B   ALTER TABLE ONLY public.vault DROP CONSTRAINT vault_user_id_fkey;
       public          postgres    false    216    3854    222            �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �      �      x������ � �     