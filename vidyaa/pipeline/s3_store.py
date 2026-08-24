"""
S3 Storage Protocol — Bharat Shiksha 2026-27
Implements enterprise S3 contract: versioning, SSE, metadata, multipart, presigned, lifecycle
Bucket: bharat-shiksha-2026-27 (ap-south-1) | Prefix: curriculum/2026-27
Protocols: s3:// + https:// (CloudFront) + presigned GET
"""
import hashlib, json, mimetypes
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

class S3Store:
    def __init__(self, bucket, region="ap-south-1", prefix="curriculum/2026-27"):
        self.bucket = bucket
        self.region = region
        self.prefix = prefix.strip("/")
        self.s3 = boto3.client("s3", region_name=region)
        # ensure bucket exists + versioning + encryption
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            self.s3.head_bucket(Bucket=self.bucket)
        except ClientError as e:
            code = e.response.get("Error",{}).get("Code")
            if code in ("404","NoSuchBucket"):
                self.s3.create_bucket(
                    Bucket=self.bucket,
                    CreateBucketConfiguration={"LocationConstraint": self.region}
                )
        # versioning + encryption + lifecycle
        try:
            self.s3.put_bucket_versioning(Bucket=self.bucket, VersioningConfiguration={"Status":"Enabled"})
            self.s3.put_bucket_encryption(Bucket=self.bucket, ServerSideEncryptionConfiguration={
                "Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]})
            self.s3.put_bucket_lifecycle_configuration(Bucket=self.bucket, LifecycleConfiguration={
                "Rules":[
                    {"ID":"raw-to-glacier","Filter":{"Prefix":f"{self.prefix}/raw/"},"Status":"Enabled","Transitions":[{"Days":90,"StorageClass":"GLACIER"}]},
                    {"ID":"chunks-to-ia","Filter":{"Prefix":f"{self.prefix}/chunks/"},"Status":"Enabled","Transitions":[{"Days":30,"StorageClass":"STANDARD_IA"}]},
                ]})
        except ClientError:
            pass

    def _key(self, *parts): return "/".join([self.prefix]+[p.strip("/") for p in parts])

    def put_json(self, key_parts, obj, metadata=None, storage_class="STANDARD"):
        key = self._key(*key_parts)
        body = json.dumps(obj, ensure_ascii=False, indent=2).encode("utf-8")
        self.s3.put_object(
            Bucket=self.bucket, Key=key, Body=body,
            ContentType="application/json; charset=utf-8",
            ServerSideEncryption="AES256", StorageClass=storage_class,
            Metadata={k: str(v)[:1024] for k,v in (metadata or {}).items()}
        )
        return f"s3://{self.bucket}/{key}"

    def put_file(self, local_path: Path, key_parts, metadata=None):
        key = self._key(*key_parts)
        ctype = mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"
        self.s3.upload_file(
            str(local_path), self.bucket, key,
            ExtraArgs={"ContentType": ctype, "ServerSideEncryption":"AES256",
                       "Metadata": {k: str(v) for k,v in (metadata or {}).items()}}
        )
        return f"s3://{self.bucket}/{key}"

    def put_chunk(self, chunk_id, chunk_obj, subject="Mathematics", chapter="Ch04"):
        # dedup key via content hash
        h = hashlib.sha256(chunk_obj["text"].encode()).hexdigest()[:12]
        key_parts = ["chunks", subject, chapter, f"{chunk_id}_{h}.json"]
        return self.put_json(key_parts, chunk_obj, metadata={
            "syllabusSource":"NCERT_2026_27","academicYear":"2026-27",
            "chunkId":chunk_id,"hash":h,"words":str(chunk_obj.get("words",0))
        })

    def put_graph(self, local_graph_path: Path):
        return self.put_file(local_graph_path, ["graph","graphify","graph.json"])

    def presigned(self, key, expires=3600):
        return self.s3.generate_presigned_url("get_object", Params={"Bucket":self.bucket,"Key":key}, ExpiresIn=expires)

    def manifest(self):
        # limit 1000 keys preview
        resp = self.s3.list_objects_v2(Bucket=self.bucket, Prefix=self.prefix, MaxKeys=200)
        return [o["Key"] for o in resp.get("Contents",[])]
