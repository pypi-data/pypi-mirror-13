# coding: utf-8
from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Enum, Index, Integer, Numeric, String, Table, Text
from sqlalchemy.schema import FetchedValue
from sqlalchemy.dialects.postgresql.base import ARRAY, INTERVAL
from sqlalchemy.ext.declarative import declarative_base

class DebVersion(UserDefinedType): 
   def get_col_spec(self): 
       return "DEBVERSION" 

   def bind_processor(self, dialect): 
       return None 

   # ' = None' is needed for sqlalchemy 0.5: 
   def result_processor(self, dialect, coltype = None): 
       return None 

Base = declarative_base()
metadata = Base.metadata


t_active_dds = Table(
    'active_dds', metadata,
    Column('id', Integer),
    Column('login', Text)
)


t_all_bugs = Table(
    'all_bugs', metadata,
    Column('id', Integer),
    Column('package', Text),
    Column('source', Text),
    Column('arrival', DateTime),
    Column('status', Text),
    Column('severity', Enum('fixed', 'wishlist', 'minor', 'normal', 'important', 'serious', 'grave', 'critical', name='bugs_severity')),
    Column('submitter', Text),
    Column('submitter_name', Text),
    Column('submitter_email', Text),
    Column('owner', Text),
    Column('owner_name', Text),
    Column('owner_email', Text),
    Column('done', Text),
    Column('done_name', Text),
    Column('done_email', Text),
    Column('done_date', DateTime),
    Column('title', Text),
    Column('last_modified', DateTime),
    Column('forwarded', Text),
    Column('affects_oldstable', Boolean),
    Column('affects_stable', Boolean),
    Column('affects_testing', Boolean),
    Column('affects_unstable', Boolean),
    Column('affects_experimental', Boolean),
    Column('affected_packages', Text),
    Column('affected_sources', Text)
)


t_all_packages = Table(
    'all_packages', metadata,
    Column('package', Text),
    Column('version', DebVersion),
    Column('architecture', Text),
    Column('maintainer', Text),
    Column('maintainer_name', Text),
    Column('maintainer_email', Text),
    Column('description', Text),
    Column('description_md5', Text),
    Column('source', Text),
    Column('source_version', DebVersion),
    Column('essential', Text),
    Column('depends', Text),
    Column('recommends', Text),
    Column('suggests', Text),
    Column('enhances', Text),
    Column('pre_depends', Text),
    Column('breaks', Text),
    Column('installed_size', Integer),
    Column('homepage', Text),
    Column('size', Integer),
    Column('build_essential', Text),
    Column('origin', Text),
    Column('sha1', Text),
    Column('replaces', Text),
    Column('section', Text),
    Column('md5sum', Text),
    Column('bugs', Text),
    Column('priority', Text),
    Column('tag', Text),
    Column('task', Text),
    Column('python_version', Text),
    Column('ruby_versions', Text),
    Column('provides', Text),
    Column('conflicts', Text),
    Column('sha256', Text),
    Column('original_maintainer', Text),
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('multi_arch', Text),
    Column('package_type', Text)
)


t_all_packages_distrelcomparch = Table(
    'all_packages_distrelcomparch', metadata,
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('architecture', Text)
)


t_all_sources = Table(
    'all_sources', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('maintainer', Text),
    Column('maintainer_name', Text),
    Column('maintainer_email', Text),
    Column('format', Text),
    Column('files', Text),
    Column('uploaders', Text),
    Column('bin', Text),
    Column('architecture', Text),
    Column('standards_version', Text),
    Column('homepage', Text),
    Column('build_depends', Text),
    Column('build_depends_indep', Text),
    Column('build_conflicts', Text),
    Column('build_conflicts_indep', Text),
    Column('priority', Text),
    Column('section', Text),
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('vcs_type', Text),
    Column('vcs_url', Text),
    Column('vcs_browser', Text),
    Column('python_version', Text),
    Column('ruby_versions', Text),
    Column('checksums_sha1', Text),
    Column('checksums_sha256', Text),
    Column('original_maintainer', Text),
    Column('dm_upload_allowed', Boolean),
    Column('testsuite', Text),
    Column('autobuild', Text),
    Column('extra_source_only', Boolean)
)


class ArchivedBug(Base):
    __tablename__ = 'archived_bugs'

    id = Column(Integer, primary_key=True)
    package = Column(Text)
    source = Column(Text)
    arrival = Column(DateTime)
    status = Column(Text)
    severity = Column(Enum('fixed', 'wishlist', 'minor', 'normal', 'important', 'serious', 'grave', 'critical', name='bugs_severity'))
    submitter = Column(Text)
    submitter_name = Column(Text)
    submitter_email = Column(Text)
    owner = Column(Text)
    owner_name = Column(Text)
    owner_email = Column(Text)
    done = Column(Text)
    done_name = Column(Text)
    done_email = Column(Text)
    done_date = Column(DateTime)
    title = Column(Text)
    last_modified = Column(DateTime)
    forwarded = Column(Text)
    affects_oldstable = Column(Boolean)
    affects_stable = Column(Boolean)
    affects_testing = Column(Boolean)
    affects_unstable = Column(Boolean)
    affects_experimental = Column(Boolean)
    affected_packages = Column(Text)
    affected_sources = Column(Text)


class ArchivedBugsBlockedby(Base):
    __tablename__ = 'archived_bugs_blockedby'

    id = Column(Integer, primary_key=True, nullable=False)
    blocker = Column(Integer, primary_key=True, nullable=False)


class ArchivedBugsBlock(Base):
    __tablename__ = 'archived_bugs_blocks'

    id = Column(Integer, primary_key=True, nullable=False)
    blocked = Column(Integer, primary_key=True, nullable=False)


class ArchivedBugsFixedIn(Base):
    __tablename__ = 'archived_bugs_fixed_in'

    id = Column(Integer, primary_key=True, nullable=False)
    version = Column(Text, primary_key=True, nullable=False)


class ArchivedBugsFoundIn(Base):
    __tablename__ = 'archived_bugs_found_in'

    id = Column(Integer, primary_key=True, nullable=False)
    version = Column(Text, primary_key=True, nullable=False)


class ArchivedBugsMergedWith(Base):
    __tablename__ = 'archived_bugs_merged_with'

    id = Column(Integer, primary_key=True, nullable=False)
    merged_with = Column(Integer, primary_key=True, nullable=False)


class ArchivedBugsPackage(Base):
    __tablename__ = 'archived_bugs_packages'

    id = Column(Integer, primary_key=True, nullable=False)
    package = Column(Text, primary_key=True, nullable=False)
    source = Column(Text)


class ArchivedBugsStamp(Base):
    __tablename__ = 'archived_bugs_stamps'

    id = Column(Integer, primary_key=True)
    update_requested = Column(BigInteger)
    db_updated = Column(BigInteger)


class ArchivedBugsTag(Base):
    __tablename__ = 'archived_bugs_tags'

    id = Column(Integer, primary_key=True, nullable=False)
    tag = Column(Text, primary_key=True, nullable=False)


class ArchivedDescription(Base):
    __tablename__ = 'archived_descriptions'

    package = Column(Text, primary_key=True, nullable=False)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    language = Column(Text, primary_key=True, nullable=False)
    description = Column(Text, primary_key=True, nullable=False)
    long_description = Column(Text, nullable=False)
    description_md5 = Column(Text, primary_key=True, nullable=False)


class ArchivedPackage(Base):
    __tablename__ = 'archived_packages'
    __table_args__ = (
        Index('archived_packages_distrelcomp_idx', 'distribution', 'release', 'component'),
    )

    package = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    architecture = Column(Text, primary_key=True, nullable=False)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    description = Column(Text)
    description_md5 = Column(Text)
    source = Column(Text, index=True)
    source_version = Column(DebVersion)
    essential = Column(Text)
    depends = Column(Text)
    recommends = Column(Text)
    suggests = Column(Text)
    enhances = Column(Text)
    pre_depends = Column(Text)
    breaks = Column(Text)
    installed_size = Column(Integer)
    homepage = Column(Text)
    size = Column(Integer)
    build_essential = Column(Text)
    origin = Column(Text)
    sha1 = Column(Text)
    replaces = Column(Text)
    section = Column(Text)
    md5sum = Column(Text)
    bugs = Column(Text)
    priority = Column(Text)
    tag = Column(Text)
    task = Column(Text)
    python_version = Column(Text)
    ruby_versions = Column(Text)
    provides = Column(Text)
    conflicts = Column(Text)
    sha256 = Column(Text)
    original_maintainer = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    multi_arch = Column(Text)


t_archived_packages_distrelcomparch = Table(
    'archived_packages_distrelcomparch', metadata,
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('architecture', Text)
)


class ArchivedPackagesSummary(Base):
    __tablename__ = 'archived_packages_summary'
    __table_args__ = (
        Index('archived_packages_summary_distrelcompsrcver_idx', 'distribution', 'release', 'component', 'source', 'source_version'),
    )

    package = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    source = Column(Text)
    source_version = Column(DebVersion)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)


class ArchivedSource(Base):
    __tablename__ = 'archived_sources'
    __table_args__ = (
        Index('archived_sources_distrelcomp_idx', 'distribution', 'release', 'component'),
    )

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    format = Column(Text)
    files = Column(Text)
    uploaders = Column(Text)
    bin = Column(Text)
    architecture = Column(Text)
    standards_version = Column(Text)
    homepage = Column(Text)
    build_depends = Column(Text)
    build_depends_indep = Column(Text)
    build_conflicts = Column(Text)
    build_conflicts_indep = Column(Text)
    priority = Column(Text)
    section = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    vcs_type = Column(Text)
    vcs_url = Column(Text)
    vcs_browser = Column(Text)
    python_version = Column(Text)
    ruby_versions = Column(Text)
    checksums_sha1 = Column(Text)
    checksums_sha256 = Column(Text)
    original_maintainer = Column(Text)
    dm_upload_allowed = Column(Boolean)
    testsuite = Column(Text)
    autobuild = Column(Text)
    extra_source_only = Column(Boolean)


t_archived_uploaders = Table(
    'archived_uploaders', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('uploader', Text),
    Column('name', Text),
    Column('email', Text),
    Index('archived_uploaders_distrelcompsrcver_idx', 'distribution', 'release', 'component', 'source', 'version')
)


t_bapase = Table(
    'bapase', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('type', Text),
    Column('bug', Integer),
    Column('description', Text),
    Column('orphaned_time', DateTime),
    Column('orphaned_age', Integer),
    Column('in_testing', Date),
    Column('testing_age', Integer),
    Column('testing_version', DebVersion),
    Column('in_unstable', Date),
    Column('unstable_age', Integer),
    Column('unstable_version', DebVersion),
    Column('sync', Date),
    Column('sync_age', Integer),
    Column('sync_version', DebVersion),
    Column('first_seen', Date),
    Column('first_seen_age', Integer),
    Column('upload_date', DateTime(True)),
    Column('upload_age', Integer),
    Column('nmu', Boolean),
    Column('nmus', BigInteger),
    Column('rc_bugs', BigInteger),
    Column('all_bugs', BigInteger),
    Column('insts', Integer),
    Column('vote', Integer),
    Column('maintainer', Text),
    Column('last_modified', DateTime),
    Column('last_modified_age', Integer)
)


class Bibref(Base):
    __tablename__ = 'bibref'

    source = Column(Text, primary_key=True, nullable=False)
    key = Column(Text, primary_key=True, nullable=False)
    value = Column(Text, nullable=False)
    package = Column(Text, primary_key=True, nullable=False, server_default=FetchedValue())
    rank = Column(Integer, primary_key=True, nullable=False)


class BlendsDependency(Base):
    __tablename__ = 'blends_dependencies'

    blend = Column(Text, primary_key=True, nullable=False)
    task = Column(Text, primary_key=True, nullable=False)
    package = Column(Text, primary_key=True, nullable=False)
    dependency = Column(String(1))
    distribution = Column(Text)
    component = Column(Text)
    provides = Column(Boolean)


class BlendsDependenciesAlternative(Base):
    __tablename__ = 'blends_dependencies_alternatives'

    blend = Column(Text, primary_key=True, nullable=False)
    task = Column(Text, primary_key=True, nullable=False)
    alternatives = Column(Text, primary_key=True, nullable=False)
    dependency = Column(String(1))
    distribution = Column(Text)
    component = Column(Text)
    contains_provides = Column(Boolean)


t_blends_dependencies_priorities = Table(
    'blends_dependencies_priorities', metadata,
    Column('dependency', String(1)),
    Column('priority', Integer)
)


class BlendsMetadatum(Base):
    __tablename__ = 'blends_metadata'

    blend = Column(Text, primary_key=True)
    blendname = Column(Text)
    projecturl = Column(Text)
    tasksprefix = Column(Text)
    homepage = Column(Text)
    aliothurl = Column(Text)
    projectlist = Column(Text)
    logourl = Column(Text)
    outputdir = Column(Text)
    datadir = Column(Text)
    vcsdir = Column(Text)
    css = Column(Text)
    advertising = Column(Text)
    pkglist = Column(Text)
    dehsmail = Column(Text)
    distribution = Column(Text)


class BlendsProspectivepackage(Base):
    __tablename__ = 'blends_prospectivepackages'

    blend = Column(Text)
    package = Column(Text, primary_key=True)
    source = Column(Text)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    changed_by = Column(Text)
    changed_by_name = Column(Text)
    changed_by_email = Column(Text)
    uploaders = Column(Text)
    description = Column(Text)
    long_description = Column(Text)
    description_md5 = Column(Text)
    homepage = Column(Text)
    component = Column(Text)
    section = Column(Text)
    priority = Column(Text)
    vcs_type = Column(Text)
    vcs_url = Column(Text)
    vcs_browser = Column(Text)
    wnpp = Column(Integer)
    wnpp_type = Column(Text)
    wnpp_desc = Column(Text)
    license = Column(Text)
    chlog_date = Column(Text)
    chlog_version = Column(DebVersion)


class BlendsTask(Base):
    __tablename__ = 'blends_tasks'

    blend = Column(Text, primary_key=True, nullable=False)
    task = Column(Text, primary_key=True, nullable=False)
    title = Column(Text)
    metapackage = Column(Boolean)
    metapackage_name = Column(Text)
    section = Column(Text)
    enhances = Column(Text)
    leaf = Column(Text)
    test_always_lang = Column(Text)
    description = Column(Text)
    long_description = Column(Text)
    hashkey = Column(Text)


class BlendsUnknownPackage(Base):
    __tablename__ = 'blends_unknown_packages'

    blend = Column(Text)
    package = Column(Text, primary_key=True)
    pkg_url = Column(Text)
    source = Column(Text)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    description = Column(Text)
    long_description = Column(Text)
    description_md5 = Column(Text)
    homepage = Column(Text)
    langauge = Column(Text)
    enhances = Column(Text)


t_bts_tags = Table(
    'bts_tags', metadata,
    Column('tag', Text),
    Column('tag_type', Text)
)


class Bug(Base):
    __tablename__ = 'bugs'

    id = Column(Integer, primary_key=True)
    package = Column(Text, index=True)
    source = Column(Text, index=True)
    arrival = Column(DateTime)
    status = Column(Text)
    severity = Column(Enum('fixed', 'wishlist', 'minor', 'normal', 'important', 'serious', 'grave', 'critical', name='bugs_severity'), index=True)
    submitter = Column(Text)
    submitter_name = Column(Text)
    submitter_email = Column(Text)
    owner = Column(Text)
    owner_name = Column(Text)
    owner_email = Column(Text)
    done = Column(Text)
    done_name = Column(Text)
    done_email = Column(Text)
    done_date = Column(DateTime)
    title = Column(Text)
    last_modified = Column(DateTime)
    forwarded = Column(Text)
    affects_oldstable = Column(Boolean)
    affects_stable = Column(Boolean)
    affects_testing = Column(Boolean)
    affects_unstable = Column(Boolean)
    affects_experimental = Column(Boolean)
    affected_packages = Column(Text)
    affected_sources = Column(Text)


class BugsBlockedby(Base):
    __tablename__ = 'bugs_blockedby'

    id = Column(Integer, primary_key=True, nullable=False)
    blocker = Column(Integer, primary_key=True, nullable=False)


class BugsBlock(Base):
    __tablename__ = 'bugs_blocks'

    id = Column(Integer, primary_key=True, nullable=False)
    blocked = Column(Integer, primary_key=True, nullable=False)


t_bugs_count = Table(
    'bugs_count', metadata,
    Column('source', Text),
    Column('rc_bugs', BigInteger),
    Column('all_bugs', BigInteger)
)


class BugsFixedIn(Base):
    __tablename__ = 'bugs_fixed_in'

    id = Column(Integer, primary_key=True, nullable=False)
    version = Column(Text, primary_key=True, nullable=False)


class BugsFoundIn(Base):
    __tablename__ = 'bugs_found_in'

    id = Column(Integer, primary_key=True, nullable=False)
    version = Column(Text, primary_key=True, nullable=False)


class BugsMergedWith(Base):
    __tablename__ = 'bugs_merged_with'

    id = Column(Integer, primary_key=True, nullable=False)
    merged_with = Column(Integer, primary_key=True, nullable=False)


class BugsPackage(Base):
    __tablename__ = 'bugs_packages'

    id = Column(Integer, primary_key=True, nullable=False)
    package = Column(Text, primary_key=True, nullable=False, index=True)
    source = Column(Text, index=True)


t_bugs_rt_affects_oldstable = Table(
    'bugs_rt_affects_oldstable', metadata,
    Column('id', Integer),
    Column('package', Text),
    Column('source', Text)
)


t_bugs_rt_affects_stable = Table(
    'bugs_rt_affects_stable', metadata,
    Column('id', Integer),
    Column('package', Text),
    Column('source', Text)
)


t_bugs_rt_affects_testing = Table(
    'bugs_rt_affects_testing', metadata,
    Column('id', Integer),
    Column('package', Text),
    Column('source', Text)
)


t_bugs_rt_affects_testing_and_unstable = Table(
    'bugs_rt_affects_testing_and_unstable', metadata,
    Column('id', Integer),
    Column('package', Text),
    Column('source', Text)
)


t_bugs_rt_affects_unstable = Table(
    'bugs_rt_affects_unstable', metadata,
    Column('id', Integer),
    Column('package', Text),
    Column('source', Text)
)


class BugsStamp(Base):
    __tablename__ = 'bugs_stamps'

    id = Column(Integer, primary_key=True)
    update_requested = Column(BigInteger)
    db_updated = Column(BigInteger)


class BugsTag(Base):
    __tablename__ = 'bugs_tags'

    id = Column(Integer, primary_key=True, nullable=False)
    tag = Column(Text, primary_key=True, nullable=False, index=True)


t_bugs_usertags = Table(
    'bugs_usertags', metadata,
    Column('email', Text),
    Column('tag', Text),
    Column('id', Integer)
)


class CarnivoreEmail(Base):
    __tablename__ = 'carnivore_emails'

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(Text, primary_key=True, nullable=False)


class CarnivoreKey(Base):
    __tablename__ = 'carnivore_keys'

    id = Column(Integer, index=True)
    key = Column(Text, primary_key=True, nullable=False)
    key_type = Column(Text, primary_key=True, nullable=False)


class CarnivoreLogin(Base):
    __tablename__ = 'carnivore_login'

    id = Column(Integer, primary_key=True)
    login = Column(Text)


class CarnivoreName(Base):
    __tablename__ = 'carnivore_names'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, primary_key=True, nullable=False)


class Ci(Base):
    __tablename__ = 'ci'

    suite = Column(Text, primary_key=True, nullable=False)
    arch = Column(Text, primary_key=True, nullable=False)
    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion)
    date = Column(DateTime)
    run_id = Column(Text)
    status = Column(Text)
    blame = Column(Text)
    previous_status = Column(Text)
    duration = Column(Integer)
    message = Column(Text)


t_debian_maintainers = Table(
    'debian_maintainers', metadata,
    Column('maintainer', Text),
    Column('maintainer_name', Text),
    Column('maintainer_email', Text),
    Column('fingerprint', Text),
    Column('package', Text),
    Column('granted_by_fingerprint', Text)
)


t_debtags = Table(
    'debtags', metadata,
    Column('package', Text, nullable=False, index=True),
    Column('tag', Text, nullable=False, index=True)
)


class Deferred(Base):
    __tablename__ = 'deferred'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    distribution = Column(Text)
    urgency = Column(Text)
    date = Column(DateTime(True))
    delayed_until = Column(DateTime)
    delay_remaining = Column(INTERVAL)
    changed_by = Column(Text)
    changed_by_name = Column(Text)
    changed_by_email = Column(Text)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    changes = Column(Text)


class DeferredArchitecture(Base):
    __tablename__ = 'deferred_architecture'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    architecture = Column(Text, primary_key=True, nullable=False)


class DeferredBinary(Base):
    __tablename__ = 'deferred_binary'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    package = Column(Text, primary_key=True, nullable=False)


class DeferredClose(Base):
    __tablename__ = 'deferred_closes'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    id = Column(Integer, primary_key=True, nullable=False)


class Deh(Base):
    __tablename__ = 'dehs'

    source = Column(Text, primary_key=True)
    unstable_version = Column(DebVersion)
    unstable_upstream = Column(Text)
    unstable_parsed_version = Column(Text)
    unstable_status = Column(Enum('error', 'uptodate', 'outdated', 'newer-in-debian', name='dehs_status'))
    unstable_last_uptodate = Column(DateTime)
    experimental_version = Column(DebVersion)
    experimental_upstream = Column(Text)
    experimental_parsed_version = Column(Text)
    experimental_status = Column(Enum('error', 'uptodate', 'outdated', 'newer-in-debian', name='dehs_status'))
    experimental_last_uptodate = Column(DateTime)


class DerivativesDescription(Base):
    __tablename__ = 'derivatives_descriptions'

    package = Column(Text, primary_key=True, nullable=False)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    language = Column(Text, primary_key=True, nullable=False)
    description = Column(Text, primary_key=True, nullable=False)
    long_description = Column(Text, nullable=False)
    description_md5 = Column(Text, primary_key=True, nullable=False)


class DerivativesPackage(Base):
    __tablename__ = 'derivatives_packages'
    __table_args__ = (
        Index('derivatives_packages_distrelcomp_idx', 'distribution', 'release', 'component'),
    )

    package = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    architecture = Column(Text, primary_key=True, nullable=False)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    description = Column(Text)
    description_md5 = Column(Text)
    source = Column(Text, index=True)
    source_version = Column(DebVersion)
    essential = Column(Text)
    depends = Column(Text)
    recommends = Column(Text)
    suggests = Column(Text)
    enhances = Column(Text)
    pre_depends = Column(Text)
    breaks = Column(Text)
    installed_size = Column(Integer)
    homepage = Column(Text)
    size = Column(Integer)
    build_essential = Column(Text)
    origin = Column(Text)
    sha1 = Column(Text)
    replaces = Column(Text)
    section = Column(Text)
    md5sum = Column(Text)
    bugs = Column(Text)
    priority = Column(Text)
    tag = Column(Text)
    task = Column(Text)
    python_version = Column(Text)
    ruby_versions = Column(Text)
    provides = Column(Text)
    conflicts = Column(Text)
    sha256 = Column(Text)
    original_maintainer = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    multi_arch = Column(Text)
    package_type = Column(Text)


t_derivatives_packages_distrelcomparch = Table(
    'derivatives_packages_distrelcomparch', metadata,
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('architecture', Text)
)


class DerivativesPackagesSummary(Base):
    __tablename__ = 'derivatives_packages_summary'
    __table_args__ = (
        Index('derivatives_packages_summary_distrelcompsrcver_idx', 'distribution', 'release', 'component', 'source', 'source_version'),
    )

    package = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    source = Column(Text)
    source_version = Column(DebVersion)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)


class DerivativesSource(Base):
    __tablename__ = 'derivatives_sources'
    __table_args__ = (
        Index('derivatives_sources_distrelcomp_idx', 'distribution', 'release', 'component'),
    )

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    format = Column(Text)
    files = Column(Text)
    uploaders = Column(Text)
    bin = Column(Text)
    architecture = Column(Text)
    standards_version = Column(Text)
    homepage = Column(Text)
    build_depends = Column(Text)
    build_depends_indep = Column(Text)
    build_conflicts = Column(Text)
    build_conflicts_indep = Column(Text)
    priority = Column(Text)
    section = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    vcs_type = Column(Text)
    vcs_url = Column(Text)
    vcs_browser = Column(Text)
    python_version = Column(Text)
    ruby_versions = Column(Text)
    checksums_sha1 = Column(Text)
    checksums_sha256 = Column(Text)
    original_maintainer = Column(Text)
    dm_upload_allowed = Column(Boolean)
    testsuite = Column(Text)
    autobuild = Column(Text)
    extra_source_only = Column(Boolean)


t_derivatives_uploaders = Table(
    'derivatives_uploaders', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('uploader', Text),
    Column('name', Text),
    Column('email', Text),
    Index('derivatives_uploaders_distrelcompsrcver_idx', 'distribution', 'release', 'component', 'source', 'version')
)


class DescriptionImport(Base):
    __tablename__ = 'description_imports'

    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    language = Column(Text, primary_key=True, nullable=False)
    translationfile = Column(Text, nullable=False)
    translationfile_sha1 = Column(Text, nullable=False)
    import_date = Column(DateTime, server_default=FetchedValue())


class Description(Base):
    __tablename__ = 'descriptions'

    package = Column(Text, primary_key=True, nullable=False)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    language = Column(Text, primary_key=True, nullable=False)
    description = Column(Text, primary_key=True, nullable=False)
    long_description = Column(Text, nullable=False)
    description_md5 = Column(Text, primary_key=True, nullable=False)


class Duck(Base):
    __tablename__ = 'duck'

    source = Column(Text, primary_key=True)


class FtpAutoreject(Base):
    __tablename__ = 'ftp_autorejects'

    tag = Column(Text, primary_key=True)
    autoreject_type = Column(Enum('lintian', name='ftp_autoreject_type'))
    autoreject_level = Column(Enum('fatal', 'nonfatal', name='ftp_autoreject_level'))


t_hints = Table(
    'hints', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('architecture', Text),
    Column('type', Text),
    Column('argument', Text),
    Column('file', Text),
    Column('comment', Text),
    Index('hints_idx', 'source', 'version')
)


class KeyPackage(Base):
    __tablename__ = 'key_packages'

    source = Column(Text, primary_key=True)
    reason = Column(Text)


t_lintian = Table(
    'lintian', metadata,
    Column('package', Text, nullable=False, index=True),
    Column('tag_type', Enum('experimental', 'overriden', 'pedantic', 'information', 'warning', 'error', name='lintian_tagtype'), nullable=False),
    Column('package_type', Text),
    Column('package_version', DebVersion),
    Column('package_arch', Text),
    Column('tag', Text, nullable=False),
    Column('information', Text)
)


t_mentors_most_recent_package_versions = Table(
    'mentors_most_recent_package_versions', metadata,
    Column('id', Numeric),
    Column('package_id', Numeric),
    Column('version', DebVersion),
    Column('maintainer', Text),
    Column('section', Text),
    Column('distribution', Text),
    Column('component', Text),
    Column('priority', Text),
    Column('uploaded', DateTime),
    Column('closes', Text)
)


t_mentors_raw_package_info = Table(
    'mentors_raw_package_info', metadata,
    Column('id', Numeric),
    Column('package_version_id', Numeric),
    Column('from_plugin', Text),
    Column('outcome', Text),
    Column('data', Text),
    Column('severity', Numeric)
)


class MentorsRawPackageVersion(Base):
    __tablename__ = 'mentors_raw_package_versions'

    id = Column(Numeric, primary_key=True)
    package_id = Column(Numeric)
    version = Column(DebVersion)
    maintainer = Column(Text)
    section = Column(Text)
    distribution = Column(Text)
    component = Column(Text)
    priority = Column(Text)
    uploaded = Column(DateTime)
    closes = Column(Text)


class MentorsRawPackage(Base):
    __tablename__ = 'mentors_raw_packages'

    id = Column(Numeric, primary_key=True)
    name = Column(Text)
    user_id = Column(Numeric)
    description = Column(Text)
    needs_sponsor = Column(Numeric)


class MentorsRawUser(Base):
    __tablename__ = 'mentors_raw_users'

    id = Column(Numeric, primary_key=True)
    name = Column(Text)
    email = Column(Text)
    gpg_id = Column(Text)


class Migration(Base):
    __tablename__ = 'migrations'

    source = Column(Text, primary_key=True)
    in_testing = Column(Date)
    testing_version = Column(DebVersion)
    in_unstable = Column(Date)
    unstable_version = Column(DebVersion)
    sync = Column(Date)
    sync_version = Column(DebVersion)
    first_seen = Column(Date)


class NewPackage(Base):
    __tablename__ = 'new_packages'

    package = Column(Text, primary_key=True, nullable=False)
    version = Column(Text, primary_key=True, nullable=False)
    architecture = Column(Text, primary_key=True, nullable=False)
    maintainer = Column(Text)
    description = Column(Text)
    source = Column(Text)
    depends = Column(Text)
    recommends = Column(Text)
    suggests = Column(Text)
    enhances = Column(Text)
    pre_depends = Column(Text)
    breaks = Column(Text)
    replaces = Column(Text)
    provides = Column(Text)
    conflicts = Column(Text)
    installed_size = Column(Integer)
    homepage = Column(Text)
    long_description = Column(Text)
    section = Column(Text)
    component = Column(Text)
    distribution = Column(Text)
    license = Column(Text)


t_new_packages_madison = Table(
    'new_packages_madison', metadata,
    Column('package', Text),
    Column('version', Text),
    Column('source', Text),
    Column('release', Text),
    Column('architecture', Text),
    Column('component', Text),
    Column('distribution', Text)
)


class NewSource(Base):
    __tablename__ = 'new_sources'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(Text, primary_key=True, nullable=False)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    format = Column(Text)
    files = Column(Text)
    uploaders = Column(Text)
    binaries = Column(Text)
    changed_by = Column(Text)
    architecture = Column(Text)
    homepage = Column(Text)
    vcs_type = Column(Text)
    vcs_url = Column(Text)
    vcs_browser = Column(Text)
    section = Column(Text)
    component = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    closes = Column(Integer)
    license = Column(Text)
    last_modified = Column(DateTime)
    queue = Column(Text)


t_new_sources_madison = Table(
    'new_sources_madison', metadata,
    Column('source', Text),
    Column('version', Text),
    Column('component', Text),
    Column('architecture', Text),
    Column('release', Text),
    Column('distribution', Text)
)


class OrphanedPackage(Base):
    __tablename__ = 'orphaned_packages'

    source = Column(Text, primary_key=True)
    type = Column(Text)
    bug = Column(Integer)
    description = Column(Text)
    orphaned_time = Column(DateTime)


class PackageRemark(Base):
    __tablename__ = 'package_remark'

    package = Column(Text, primary_key=True)
    remark = Column(Text)


class PackageRemoval(Base):
    __tablename__ = 'package_removal'

    batch_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    arch_array = Column(ARRAY(TEXT()))


class PackageRemovalBatch(Base):
    __tablename__ = 'package_removal_batch'

    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    ftpmaster = Column(Text)
    distribution = Column(Text)
    requestor = Column(Text)
    reasons = Column(Text)


class Package(Base):
    __tablename__ = 'packages'
    __table_args__ = (
        Index('packages_distrelcomp_idx', 'distribution', 'release', 'component'),
        Index('packages_pkgverdescr_idx', 'package', 'version', 'description')
    )

    package = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    architecture = Column(Text, primary_key=True, nullable=False)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    description = Column(Text)
    description_md5 = Column(Text)
    source = Column(Text, index=True)
    source_version = Column(DebVersion)
    essential = Column(Text)
    depends = Column(Text)
    recommends = Column(Text)
    suggests = Column(Text)
    enhances = Column(Text)
    pre_depends = Column(Text)
    breaks = Column(Text)
    installed_size = Column(Integer)
    homepage = Column(Text)
    size = Column(Integer)
    build_essential = Column(Text)
    origin = Column(Text)
    sha1 = Column(Text)
    replaces = Column(Text)
    section = Column(Text)
    md5sum = Column(Text)
    bugs = Column(Text)
    priority = Column(Text)
    tag = Column(Text)
    task = Column(Text)
    python_version = Column(Text)
    ruby_versions = Column(Text)
    provides = Column(Text)
    conflicts = Column(Text)
    sha256 = Column(Text)
    original_maintainer = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    multi_arch = Column(Text)
    package_type = Column(Text)


t_packages_distrelcomparch = Table(
    'packages_distrelcomparch', metadata,
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('architecture', Text)
)


class PackagesSummary(Base):
    __tablename__ = 'packages_summary'
    __table_args__ = (
        Index('packages_summary_distrelcompsrcver_idx', 'distribution', 'release', 'component', 'source', 'source_version'),
    )

    package = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    source = Column(Text)
    source_version = Column(DebVersion)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)


t_piuparts_status = Table(
    'piuparts_status', metadata,
    Column('section', Text, index=True),
    Column('source', Text, index=True),
    Column('version', Text),
    Column('status', Text, index=True)
)


class Popcon(Base):
    __tablename__ = 'popcon'

    package = Column(Text, primary_key=True)
    insts = Column(Integer)
    vote = Column(Integer)
    olde = Column(Integer)
    recent = Column(Integer)
    nofiles = Column(Integer)


class PopconSrc(Base):
    __tablename__ = 'popcon_src'

    source = Column(Text, primary_key=True)
    insts = Column(Integer)
    vote = Column(Integer)
    olde = Column(Integer)
    recent = Column(Integer)
    nofiles = Column(Integer)


class PopconSrcAverage(Base):
    __tablename__ = 'popcon_src_average'

    source = Column(Text, primary_key=True)
    insts = Column(Integer)
    vote = Column(Integer)
    olde = Column(Integer)
    recent = Column(Integer)
    nofiles = Column(Integer)


t_potential_bug_closures = Table(
    'potential_bug_closures', metadata,
    Column('id', Integer, index=True),
    Column('source', Text, index=True),
    Column('distribution', Text),
    Column('origin', Text)
)


class PseudoPackage(Base):
    __tablename__ = 'pseudo_packages'

    package = Column(Text, primary_key=True)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    description = Column(Text)


class Release(Base):
    __tablename__ = 'releases'

    release = Column(Text, primary_key=True)
    releasedate = Column(Date)
    role = Column(Text)
    releaseversion = Column(Text)
    distribution = Column(Text)
    sort = Column(Integer)


t_relevant_hints = Table(
    'relevant_hints', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('architecture', Text),
    Column('type', Text),
    Column('argument', Text),
    Column('file', Text),
    Column('comment', Text)
)


class Reproducible(Base):
    __tablename__ = 'reproducible'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion)
    release = Column(Text, primary_key=True, nullable=False)
    architecture = Column(Text, primary_key=True, nullable=False)
    status = Column(Text)


class Screenshot(Base):
    __tablename__ = 'screenshots'

    package = Column(Text, nullable=False)
    version = Column(Text)
    homepage = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    description = Column(Text)
    section = Column(Text)
    screenshot_url = Column(Text, nullable=False)
    large_image_url = Column(Text, nullable=False)
    small_image_url = Column(Text, primary_key=True)


class SecurityIssue(Base):
    __tablename__ = 'security_issues'

    source = Column(Text, primary_key=True, nullable=False)
    issue = Column(Text, primary_key=True, nullable=False)
    description = Column(Text)
    scope = Column(Enum('local', 'remote', name='security_issues_scope'))
    bug = Column(Integer)


class SecurityIssuesRelease(Base):
    __tablename__ = 'security_issues_releases'

    source = Column(Text, primary_key=True, nullable=False)
    issue = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    fixed_version = Column(Text)
    status = Column(Enum('open', 'resolved', 'undetermined', name='security_issues_releases_status'))
    urgency = Column(Text)
    nodsa = Column(Text)


class Source(Base):
    __tablename__ = 'sources'
    __table_args__ = (
        Index('sources_distrelcomp_idx', 'distribution', 'release', 'component'),
    )

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    format = Column(Text)
    files = Column(Text)
    uploaders = Column(Text)
    bin = Column(Text)
    architecture = Column(Text)
    standards_version = Column(Text)
    homepage = Column(Text)
    build_depends = Column(Text)
    build_depends_indep = Column(Text)
    build_conflicts = Column(Text)
    build_conflicts_indep = Column(Text)
    priority = Column(Text)
    section = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False, index=True)
    component = Column(Text, primary_key=True, nullable=False)
    vcs_type = Column(Text)
    vcs_url = Column(Text)
    vcs_browser = Column(Text)
    python_version = Column(Text)
    ruby_versions = Column(Text)
    checksums_sha1 = Column(Text)
    checksums_sha256 = Column(Text)
    original_maintainer = Column(Text)
    dm_upload_allowed = Column(Boolean)
    testsuite = Column(Text)
    autobuild = Column(Text)
    extra_source_only = Column(Boolean)


t_sources_popcon = Table(
    'sources_popcon', metadata,
    Column('source', Text),
    Column('insts', Integer),
    Column('vote', Integer),
    Column('olde', Integer),
    Column('recent', Integer),
    Column('nofiles', Integer)
)


t_sources_redundant = Table(
    'sources_redundant', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('maintainer', Text),
    Column('maintainer_name', Text),
    Column('maintainer_email', Text),
    Column('format', Text),
    Column('files', Text),
    Column('uploaders', Text),
    Column('bin', Text),
    Column('architecture', Text),
    Column('standards_version', Text),
    Column('homepage', Text),
    Column('build_depends', Text),
    Column('build_depends_indep', Text),
    Column('build_conflicts', Text),
    Column('build_conflicts_indep', Text),
    Column('priority', Text),
    Column('section', Text),
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('vcs_type', Text),
    Column('vcs_url', Text),
    Column('vcs_browser', Text),
    Column('python_version', Text),
    Column('ruby_versions', Text),
    Column('checksums_sha1', Text),
    Column('checksums_sha256', Text),
    Column('original_maintainer', Text),
    Column('dm_upload_allowed', Boolean),
    Column('testsuite', Text),
    Column('autobuild', Text),
    Column('extra_source_only', Boolean)
)


t_sources_uniq = Table(
    'sources_uniq', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('maintainer', Text),
    Column('maintainer_name', Text),
    Column('maintainer_email', Text),
    Column('format', Text),
    Column('files', Text),
    Column('uploaders', Text),
    Column('bin', Text),
    Column('architecture', Text),
    Column('standards_version', Text),
    Column('homepage', Text),
    Column('build_depends', Text),
    Column('build_depends_indep', Text),
    Column('build_conflicts', Text),
    Column('build_conflicts_indep', Text),
    Column('priority', Text),
    Column('section', Text),
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('vcs_type', Text),
    Column('vcs_url', Text),
    Column('vcs_browser', Text),
    Column('python_version', Text),
    Column('ruby_versions', Text),
    Column('checksums_sha1', Text),
    Column('checksums_sha256', Text),
    Column('original_maintainer', Text),
    Column('dm_upload_allowed', Boolean),
    Column('testsuite', Text),
    Column('autobuild', Text),
    Column('extra_source_only', Boolean)
)


t_sponsorship_requests = Table(
    'sponsorship_requests', metadata,
    Column('id', Integer),
    Column('source', Text),
    Column('version', Text),
    Column('title', Text)
)


t_testing_autoremovals = Table(
    'testing_autoremovals', metadata,
    Column('source', Text, index=True),
    Column('version', Text),
    Column('bugs', Text),
    Column('first_seen', BigInteger),
    Column('last_checked', BigInteger),
    Column('removal_time', BigInteger),
    Column('rdeps', Text),
    Column('buggy_deps', Text),
    Column('bugs_deps', Text),
    Column('rdeps_popcon', BigInteger)
)


class Timestamp(Base):
    __tablename__ = 'timestamps'

    id = Column(Integer, primary_key=True, server_default=FetchedValue())
    source = Column(Text)
    command = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class UbuntuBug(Base):
    __tablename__ = 'ubuntu_bugs'

    bug = Column(Integer, primary_key=True)
    title = Column(Text)
    reporter_login = Column(Text)
    reporter_name = Column(Text)
    duplicate_of = Column(Integer)
    date_reported = Column(Text)
    date_updated = Column(Text)
    security = Column(Boolean)
    patches = Column(Boolean)


class UbuntuBugsDuplicate(Base):
    __tablename__ = 'ubuntu_bugs_duplicates'

    bug = Column(Integer, primary_key=True, nullable=False, index=True)
    duplicate = Column(Integer, primary_key=True, nullable=False)


t_ubuntu_bugs_subscribers = Table(
    'ubuntu_bugs_subscribers', metadata,
    Column('bug', Integer, index=True),
    Column('subscriber_login', Text),
    Column('subscriber_name', Text)
)


class UbuntuBugsTag(Base):
    __tablename__ = 'ubuntu_bugs_tags'

    bug = Column(Integer, primary_key=True, nullable=False, index=True)
    tag = Column(Text, primary_key=True, nullable=False)


class UbuntuBugsTask(Base):
    __tablename__ = 'ubuntu_bugs_tasks'

    bug = Column(Integer, primary_key=True, nullable=False, index=True)
    package = Column(Text, primary_key=True, nullable=False, index=True)
    distro = Column(Text, primary_key=True, nullable=False)
    status = Column(Text)
    importance = Column(Text)
    component = Column(Text)
    milestone = Column(Text)
    date_created = Column(Text)
    date_assigned = Column(Text)
    date_closed = Column(Text)
    date_incomplete = Column(Text)
    date_confirmed = Column(Text)
    date_inprogress = Column(Text)
    date_fix_committed = Column(Text)
    date_fix_released = Column(Text)
    date_left_new = Column(Text)
    date_triaged = Column(Text)
    date_left_closed = Column(Text)
    watch = Column(Text)
    reporter_login = Column(Text)
    reporter_name = Column(Text)
    assignee_login = Column(Text)
    assignee_name = Column(Text)


class UbuntuDescriptionImport(Base):
    __tablename__ = 'ubuntu_description_imports'

    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    language = Column(Text, primary_key=True, nullable=False)
    translationfile = Column(Text, nullable=False)
    translationfile_sha1 = Column(Text, nullable=False)
    import_date = Column(DateTime, server_default=FetchedValue())


class UbuntuDescription(Base):
    __tablename__ = 'ubuntu_descriptions'

    package = Column(Text, primary_key=True, nullable=False)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    language = Column(Text, primary_key=True, nullable=False)
    description = Column(Text, primary_key=True, nullable=False)
    long_description = Column(Text, nullable=False)
    description_md5 = Column(Text, primary_key=True, nullable=False)


t_ubuntu_lintian = Table(
    'ubuntu_lintian', metadata,
    Column('package', Text, nullable=False),
    Column('tag_type', Enum('experimental', 'overriden', 'pedantic', 'information', 'warning', 'error', name='lintian_tagtype'), nullable=False),
    Column('package_type', Text),
    Column('package_version', DebVersion),
    Column('package_arch', Text),
    Column('tag', Text, nullable=False),
    Column('information', Text)
)


class UbuntuPackage(Base):
    __tablename__ = 'ubuntu_packages'
    __table_args__ = (
        Index('ubuntu_packages_distrelcomp_idx', 'distribution', 'release', 'component'),
    )

    package = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    architecture = Column(Text, primary_key=True, nullable=False)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    description = Column(Text)
    description_md5 = Column(Text)
    source = Column(Text, index=True)
    source_version = Column(DebVersion)
    essential = Column(Text)
    depends = Column(Text)
    recommends = Column(Text)
    suggests = Column(Text)
    enhances = Column(Text)
    pre_depends = Column(Text)
    breaks = Column(Text)
    installed_size = Column(Integer)
    homepage = Column(Text)
    size = Column(Integer)
    build_essential = Column(Text)
    origin = Column(Text)
    sha1 = Column(Text)
    replaces = Column(Text)
    section = Column(Text)
    md5sum = Column(Text)
    bugs = Column(Text)
    priority = Column(Text)
    tag = Column(Text)
    task = Column(Text)
    python_version = Column(Text)
    ruby_versions = Column(Text)
    provides = Column(Text)
    conflicts = Column(Text)
    sha256 = Column(Text)
    original_maintainer = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    multi_arch = Column(Text)
    package_type = Column(Text)


t_ubuntu_packages_distrelcomparch = Table(
    'ubuntu_packages_distrelcomparch', metadata,
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('architecture', Text)
)


class UbuntuPackagesSummary(Base):
    __tablename__ = 'ubuntu_packages_summary'
    __table_args__ = (
        Index('ubuntu_packages_summary_distrelcompsrcver_idx', 'distribution', 'release', 'component', 'source', 'source_version'),
    )

    package = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    source = Column(Text)
    source_version = Column(DebVersion)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)


class UbuntuPopcon(Base):
    __tablename__ = 'ubuntu_popcon'

    package = Column(Text, primary_key=True)
    insts = Column(Integer)
    vote = Column(Integer)
    olde = Column(Integer)
    recent = Column(Integer)
    nofiles = Column(Integer)


class UbuntuPopconSrc(Base):
    __tablename__ = 'ubuntu_popcon_src'

    source = Column(Text, primary_key=True)
    insts = Column(Integer)
    vote = Column(Integer)
    olde = Column(Integer)
    recent = Column(Integer)
    nofiles = Column(Integer)


class UbuntuPopconSrcAverage(Base):
    __tablename__ = 'ubuntu_popcon_src_average'

    source = Column(Text, primary_key=True)
    insts = Column(Integer)
    vote = Column(Integer)
    olde = Column(Integer)
    recent = Column(Integer)
    nofiles = Column(Integer)


class UbuntuSource(Base):
    __tablename__ = 'ubuntu_sources'
    __table_args__ = (
        Index('ubuntu_sources_distrelcomp_idx', 'distribution', 'release', 'component'),
    )

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    format = Column(Text)
    files = Column(Text)
    uploaders = Column(Text)
    bin = Column(Text)
    architecture = Column(Text)
    standards_version = Column(Text)
    homepage = Column(Text)
    build_depends = Column(Text)
    build_depends_indep = Column(Text)
    build_conflicts = Column(Text)
    build_conflicts_indep = Column(Text)
    priority = Column(Text)
    section = Column(Text)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    vcs_type = Column(Text)
    vcs_url = Column(Text)
    vcs_browser = Column(Text)
    python_version = Column(Text)
    ruby_versions = Column(Text)
    checksums_sha1 = Column(Text)
    checksums_sha256 = Column(Text)
    original_maintainer = Column(Text)
    dm_upload_allowed = Column(Boolean)
    testsuite = Column(Text)
    autobuild = Column(Text)
    extra_source_only = Column(Boolean)


t_ubuntu_sources_popcon = Table(
    'ubuntu_sources_popcon', metadata,
    Column('source', Text),
    Column('insts', Integer),
    Column('vote', Integer),
    Column('olde', Integer),
    Column('recent', Integer),
    Column('nofiles', Integer)
)


class UbuntuUploadHistory(Base):
    __tablename__ = 'ubuntu_upload_history'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    date = Column(DateTime(True))
    changed_by = Column(Text)
    changed_by_name = Column(Text)
    changed_by_email = Column(Text)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    nmu = Column(Boolean)
    signed_by = Column(Text)
    signed_by_name = Column(Text)
    signed_by_email = Column(Text)
    key_id = Column(Text)
    distribution = Column(Text)
    component = Column(Text)
    file = Column(Text)
    fingerprint = Column(Text)
    original_maintainer = Column(Text)
    original_maintainer_name = Column(Text)
    original_maintainer_email = Column(Text)


class UbuntuUploadHistoryClose(Base):
    __tablename__ = 'ubuntu_upload_history_closes'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    bug = Column(Integer, primary_key=True, nullable=False)
    file = Column(Text)


class UbuntuUploadHistoryLaunchpadClose(Base):
    __tablename__ = 'ubuntu_upload_history_launchpad_closes'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    bug = Column(Integer, primary_key=True, nullable=False)
    file = Column(Text)


t_ubuntu_uploaders = Table(
    'ubuntu_uploaders', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('uploader', Text),
    Column('name', Text),
    Column('email', Text),
    Index('ubuntu_uploaders_distrelcompsrcver_idx', 'distribution', 'release', 'component', 'source', 'version')
)


class UddLog(Base):
    __tablename__ = 'udd_logs'

    importer = Column(Text, primary_key=True, nullable=False)
    time = Column(DateTime(True), primary_key=True, nullable=False)
    duration = Column(Integer)
    status = Column(Integer)
    log = Column(Text)


class UploadHistory(Base):
    __tablename__ = 'upload_history'
    __table_args__ = (
        Index('upload_history_distribution_date_idx', 'distribution', 'date'),
    )

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    date = Column(DateTime(True))
    changed_by = Column(Text)
    changed_by_name = Column(Text)
    changed_by_email = Column(Text)
    maintainer = Column(Text)
    maintainer_name = Column(Text)
    maintainer_email = Column(Text)
    nmu = Column(Boolean)
    signed_by = Column(Text)
    signed_by_name = Column(Text)
    signed_by_email = Column(Text)
    key_id = Column(Text)
    distribution = Column(Text)
    file = Column(Text)
    fingerprint = Column(Text, index=True)


class UploadHistoryArchitecture(Base):
    __tablename__ = 'upload_history_architecture'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    architecture = Column(Text, primary_key=True, nullable=False)
    file = Column(Text)


class UploadHistoryClose(Base):
    __tablename__ = 'upload_history_closes'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    bug = Column(Integer, primary_key=True, nullable=False)
    file = Column(Text)


t_upload_history_nmus = Table(
    'upload_history_nmus', metadata,
    Column('source', Text),
    Column('nmus', BigInteger)
)


t_uploaders = Table(
    'uploaders', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('uploader', Text),
    Column('name', Text),
    Column('email', Text),
    Index('uploaders_distrelcompsrcver_idx', 'distribution', 'release', 'component', 'source', 'version')
)


class Upstream(Base):
    __tablename__ = 'upstream'

    source = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion, primary_key=True, nullable=False)
    distribution = Column(Text, primary_key=True, nullable=False)
    release = Column(Text, primary_key=True, nullable=False)
    component = Column(Text, primary_key=True, nullable=False)
    watch_file = Column(Text)
    signing_key_pgp = Column(Text)
    signing_key_asc = Column(Text)
    debian_uversion = Column(Text)
    debian_mangled_uversion = Column(Text)
    upstream_version = Column(Text)
    upstream_url = Column(Text)
    errors = Column(Text)
    warnings = Column(Text)
    status = Column(Text)
    last_check = Column(DateTime)


t_upstream_status = Table(
    'upstream_status', metadata,
    Column('source', Text),
    Column('version', DebVersion),
    Column('distribution', Text),
    Column('release', Text),
    Column('component', Text),
    Column('watch_file', Text),
    Column('debian_uversion', Text),
    Column('debian_mangled_uversion', Text),
    Column('upstream_version', Text),
    Column('upstream_url', Text),
    Column('errors', Text),
    Column('warnings', Text),
    Column('status', Text),
    Column('last_check', DateTime)
)


class Vc(Base):
    __tablename__ = 'vcs'

    source = Column(Text, primary_key=True)
    team = Column(Text)
    version = Column(DebVersion)
    distribution = Column(Text)


class Vcswatch(Base):
    __tablename__ = 'vcswatch'

    source = Column(Text, primary_key=True)
    version = Column(DebVersion)
    vcs = Column(Text)
    url = Column(Text)
    branch = Column(Text)
    browser = Column(Text)
    last_scan = Column(DateTime(True))
    next_scan = Column(DateTime(True), server_default=FetchedValue())
    status = Column(Text, server_default=FetchedValue())
    debian_dir = Column(Boolean, server_default=FetchedValue())
    changelog_version = Column(DebVersion)
    changelog_distribution = Column(Text)
    changelog = Column(Text)
    error = Column(Text)


class Wannabuild(Base):
    __tablename__ = 'wannabuild'

    source = Column(Text, primary_key=True, nullable=False)
    distribution = Column(Text, primary_key=True, nullable=False)
    architecture = Column(Text, primary_key=True, nullable=False)
    version = Column(DebVersion)
    state = Column(Text)
    installed_version = Column(DebVersion)
    previous_state = Column(Text)
    state_change = Column(DateTime)
    binary_nmu_version = Column(Numeric)
    notes = Column(Text)
    vancouvered = Column(Boolean)


t_wnpp = Table(
    'wnpp', metadata,
    Column('id', Integer),
    Column('type', Text),
    Column('source', Text),
    Column('title', Text)
)
